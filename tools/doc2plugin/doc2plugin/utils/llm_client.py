"""
LLM 客户端模块 - 基于 LangChain 原生能力

功能特性：
1. 自动重试机制（基于 with_retry，支持指数退避）
2. 流式输出支持（实时回调更新终端）
3. 完整的日志记录（Callbacks 机制）
4. 输出解析支持（JSON、代码块等）
5. 统一的错误处理
6. Token统计（基于tiktoken估算）
"""

import os
import logging
from typing import List, Optional, Any, Dict
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI

from doc2plugin.utils.terminal_output import terminal


def estimate_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    估算文本的token数量
    
    使用tiktoken库进行token估算。如果tiktoken不可用，使用简单的字符数估算：
    - 英文：约4个字符 = 1个token
    - 中文：约1.5个字符 = 1个token
    - 混合文本：按平均2.5个字符 = 1个token估算
    
    Args:
        text: 要估算的文本
        model: 模型名称，用于选择合适的tokenizer
        
    Returns:
        估算的token数量
    """
    if not text:
        return 0
    
    try:
        import tiktoken
        
        # 根据模型选择编码器
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # 如果模型不在已知列表中，使用cl100k_base（GPT-3.5/GPT-4的编码器）
            encoding = tiktoken.get_encoding("cl100k_base")
        
        return len(encoding.encode(text))
    
    except ImportError:
        # 如果tiktoken不可用，使用简单估算
        # 统计中文字符（CJK字符）和其他字符
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        
        # 中文约1.5字符=1token，英文约4字符=1token
        estimated_tokens = int(chinese_chars / 1.5 + other_chars / 4)
        
        return max(estimated_tokens, 1)  # 至少返回1


class StreamingCallbackHandler(BaseCallbackHandler):
    """流式输出回调处理器 - 将流式内容显示到终端"""
    
    def __init__(self):
        self.content = ""
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """当收到新token时调用"""
        self.content += token
        terminal.update_streaming_content(self.content)


class LoggingCallbackHandler(BaseCallbackHandler):
    """日志记录回调处理器 - 记录 LLM 交互到日志文件"""
    
    def __init__(self, logger: logging.Logger, llm_logger: Optional[logging.Logger] = None, stage: str = "未知阶段"):
        self.logger = logger
        self.llm_logger = llm_logger
        self.stage = stage
        self.output_content = ""
        self.attempt = 1
        self.total_input_tokens = 0
    
    def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], **kwargs) -> None:
        """Chat模型开始时"""
        if self.llm_logger:
            self.llm_logger.info(f"=== LLM输入 ({self.stage}) ===")
        
        self.total_input_tokens = 0
        total_input_chars = 0
        
        for i, message_list in enumerate(messages):
            for j, message in enumerate(message_list):
                content = message.content
                message_type = message.__class__.__name__
                
                if self.llm_logger:
                    self.llm_logger.info(f"消息 {i+1}.{j+1} [{message_type}]:")
                    self.llm_logger.info(content)
                
                # 统计字符数和token数
                input_chars = len(content)
                input_tokens = estimate_tokens(content)
                total_input_chars += input_chars
                self.total_input_tokens += input_tokens
                
                self.logger.info(f"LLM调用 ({self.stage}) - 输入消息 {i+1}.{j+1}: {input_chars} 字符, 约 {input_tokens} tokens")
        
        # 记录总计
        self.logger.info(f"LLM调用 ({self.stage}) - 输入总计: {total_input_chars} 字符, 约 {self.total_input_tokens} tokens")
        if self.llm_logger:
            self.llm_logger.info(f"输入总计: {total_input_chars} 字符, 约 {self.total_input_tokens} tokens")
    
    def on_llm_end(self, response, **kwargs) -> None:
        """LLM 结束时"""
        if hasattr(response, 'generations') and response.generations:
            generation = response.generations[0][0]
            if hasattr(generation, 'text'):
                self.output_content = generation.text
            elif hasattr(generation, 'message'):
                self.output_content = generation.message.content
        
        output_chars = len(self.output_content)
        output_tokens = estimate_tokens(self.output_content)
        
        # 计算总token消耗
        total_tokens = self.total_input_tokens + output_tokens
        
        self.logger.info(f"LLM调用 ({self.stage}) - 输出: {output_chars} 字符, 约 {output_tokens} tokens")
        
        if self.llm_logger:
            self.llm_logger.info(f"=== LLM输出 ({self.stage}) ===")
            self.llm_logger.info(f"响应长度: {output_chars} 字符, 约 {output_tokens} tokens")
            self.llm_logger.info("响应内容:")
            self.llm_logger.info(self.output_content)
            self.llm_logger.info(f"=== LLM输出结束 ({self.stage}) ===")
    
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """LLM 错误时"""
        self.logger.error(f"LLM调用错误 ({self.stage}): {error}")
        if self.llm_logger:
            self.llm_logger.error(f"LLM调用错误 ({self.stage}): {error}")


class LLMClient:
    """
    LLM客户端 - 基于 LangChain 原生能力
    
    充分利用 LangChain 的：
    - 自动重试（with_retry）
    - 流式输出（stream）
    - Callbacks（日志和统计）
    - 输出解析（OutputParsers）
    """
    
    def __init__(
        self, 
        llm: ChatOpenAI,
        logger: logging.Logger,
        llm_logger: Optional[logging.Logger] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        初始化LLM客户端
        
        Args:
            llm: LangChain的ChatOpenAI实例
            logger: 主日志记录器（用于agent.log）
            llm_logger: LLM专用日志记录器（用于llm.log），可选
            max_retries: 最大重试次数
            retry_delay: 初始重试延迟（秒）
        """
        self.llm = llm
        self.logger = logger
        self.llm_logger = llm_logger
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # 配置重试
        self.llm_with_retry = self.llm.with_retry(
            stop_after_attempt=max_retries + 1,
            wait_exponential_jitter=True
        )
    
    def invoke_with_streaming(
        self, 
        messages: List[BaseMessage], 
        spinner_message: str = "正在调用大模型...",
        stage: str = "未知阶段",
        output_parser: Optional[Any] = None
    ) -> str:
        """
        使用流式输出调用LLM
        
        Args:
            messages: 消息列表
            spinner_message: 旋转动画显示的消息
            stage: 调用阶段标识（用于日志记录）
            output_parser: 输出解析器（可选），如 JsonOutputParser()
            
        Returns:
            完整的LLM响应内容
        """
        streaming_handler = StreamingCallbackHandler()
        logging_handler = LoggingCallbackHandler(self.logger, self.llm_logger, stage)
        
        try:
            full_response = ""
            
            with terminal.spinner(spinner_message):
                for chunk in self.llm_with_retry.stream(
                    messages,
                    config={"callbacks": [streaming_handler, logging_handler]}
                ):
                    if chunk.content:
                        full_response += chunk.content
            
            # 如果提供了输出解析器，进行解析
            if output_parser:
                try:
                    parsed = output_parser.parse(full_response)
                    if isinstance(output_parser, JsonOutputParser):
                        import json
                        return json.dumps(parsed, ensure_ascii=False, indent=2)
                    return str(parsed)
                except Exception as e:
                    self.logger.warning(f"输出解析失败: {e}，返回原始内容")
                    return full_response
            
            return full_response
            
        except Exception as e:
            self.logger.error(f"LLM调用失败 ({stage}): {e}")
            terminal.error(f"LLM调用失败: {e}")
            raise


class CodeBlockOutputParser:
    """
    代码块输出解析器 - 从LLM响应中提取代码块
    
    利用 LangChain 的解析器模式，支持提取：
    - bash/shell 脚本
    - markdown 文档
    - 任意语言代码块
    """
    
    def __init__(self, language: Optional[str] = None):
        """
        初始化代码块解析器
        
        Args:
            language: 要提取的语言类型（如 'bash', 'python', 'markdown'），
                     如果为 None，则提取最长的代码块
        """
        self.language = language
    
    def parse(self, text: str) -> str:
        """
        解析文本，提取代码块
        
        Args:
            text: LLM响应文本
            
        Returns:
            提取的代码内容
        """
        import re
        
        # 如果指定了语言，优先提取该语言的代码块
        if self.language:
            patterns = [
                rf'```{self.language}\n(.*?)```',
                rf'```{self.language.lower()}\n(.*?)```',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.DOTALL)
                if matches:
                    # 返回最长的匹配
                    return max(matches, key=len).strip()
        
        # 尝试提取任何代码块
        pattern = r'```(?:\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            return max(matches, key=len).strip()
        
        # 特殊处理：如果是脚本且以shebang开头
        if text.strip().startswith('#!'):
            return text.strip()
        
        # 特殊处理：如果是markdown且包含标题
        if any(marker in text for marker in ['# ', '## ', '### ']):
            return text.strip()
        
        # 返回原始内容
        return text.strip()


def setup_llm_logger(log_dir: str) -> logging.Logger:
    """
    设置LLM专用日志记录器
    
    Args:
        log_dir: 日志目录路径
        
    Returns:
        配置好的LLM日志记录器
    """
    llm_logger = logging.getLogger('doc2plugin.agent.llm')
    llm_logger.setLevel(logging.INFO)
    llm_logger.handlers.clear()
    
    llm_handler = logging.FileHandler(
        os.path.join(log_dir, 'llm.log'),
        encoding='utf-8'
    )
    llm_handler.setLevel(logging.INFO)
    
    llm_formatter = logging.Formatter(
        '[%(asctime)s - LLM - %(levelname)s] %(message)s'
    )
    llm_handler.setFormatter(llm_formatter)
    
    llm_logger.addHandler(llm_handler)
    llm_logger.propagate = False
    
    return llm_logger
