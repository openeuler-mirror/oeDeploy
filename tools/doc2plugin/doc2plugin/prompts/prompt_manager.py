"""
提示词管理器 - 使用 LangChain 的 ChatPromptTemplate

充分利用 LangChain 的提示词管理能力，包括：
- ChatPromptTemplate 进行结构化提示词管理
- MessagesPlaceholder 支持动态消息注入
- 变量替换和格式化
"""

from typing import Optional, List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from doc2plugin.prompts.system_prompts import SystemPromptBuilder
from doc2plugin.prompts.task_prompts import TaskPromptBuilder
from doc2plugin.prompts.document_prompts import DocumentPromptBuilder


class PromptManager:
    """
    提示词管理器 - 基于 LangChain 的 ChatPromptTemplate
    
    利用 LangChain 的提示词模板系统，提供更好的组织和管理。
    """
    
    def __init__(self, develop_doc_content: Optional[str] = None, mode_prompt: Optional[List[str]] = None):
        """
        初始化提示词管理器
        
        Args:
            develop_doc_content: 开发文档内容（用于文档驱动模式）
            mode_prompt: 模式专用提示词列表（高优先级）
        """
        self.develop_doc_content = develop_doc_content
        self.mode_prompt = mode_prompt or []
        
        # 初始化各个提示词构建器
        self.system_builder = SystemPromptBuilder(develop_doc_content, mode_prompt)
        self.task_builder = TaskPromptBuilder()
        self.document_builder = DocumentPromptBuilder()
        
        # 缓存常用的 prompt templates
        self._system_prompt_cache = {}
    
    def get_system_prompt(self, mode: str = "shell") -> str:
        """
        获取系统提示词
        
        Args:
            mode: 模式类型（shell 或其他文档驱动的模式）
            
        Returns:
            系统提示词字符串
        """
        # 使用缓存避免重复构建
        if mode not in self._system_prompt_cache:
            self._system_prompt_cache[mode] = self.system_builder.build_system_prompt(mode)
        
        return self._system_prompt_cache[mode]
    
    def create_chat_prompt(self, mode: str, human_message: str) -> ChatPromptTemplate:
        """
        创建一个完整的 ChatPromptTemplate
        
        Args:
            mode: 模式类型
            human_message: 人类消息内容
            
        Returns:
            ChatPromptTemplate 实例
        """
        system_prompt = self.get_system_prompt(mode)
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_message)
        ])
    
    def format_messages(self, mode: str, human_message: str, **kwargs) -> List:
        """
        格式化消息列表（用于直接传递给 LLM）
        
        Args:
            mode: 模式类型
            human_message: 人类消息内容
            **kwargs: 额外的格式化变量
            
        Returns:
            消息列表
        """
        system_prompt = self.get_system_prompt(mode)
        
        # 如果 human_message 中包含变量占位符，进行格式化
        if kwargs:
            try:
                human_message = human_message.format(**kwargs)
            except KeyError as e:
                print(f"警告：提示词格式化时缺少变量：{e}")
        
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
    
    # ==================== 任务相关提示词 ====================
    
    def get_task_planning_prompt_structured(self, context) -> str:
        """
        获取任务规划提示词（结构化配置版本）
        
        Args:
            context: LLMContextConfig对象
        """
        has_doc = context.develop_doc_content is not None
        return self.task_builder.build_task_planning_prompt(
            context.target, 
            context.prompt,
            context.mode,
            has_doc
        )
    
    def get_task_adjustment_prompt(self, current_tasks: str, issue_description: str) -> str:
        """获取任务调整提示词"""
        return self.task_builder.build_task_adjustment_prompt(current_tasks, issue_description)
    
    def get_task_retry_prompt(self, task_name: str, error_message: str, retry_count: int) -> str:
        """获取任务重试提示词"""
        return self.task_builder.build_task_retry_prompt(task_name, error_message, retry_count)
    
    def get_quality_check_prompt(self) -> str:
        """获取质量检查提示词"""
        return self.task_builder.build_quality_check_prompt()
    
    # ==================== 文档相关提示词 ====================
    
    def get_document_refinement_prompt(self, task_target: str, task_prompt: str) -> str:
        """获取文档提纯提示词"""
        return self.document_builder.build_document_refinement_prompt(task_target, task_prompt)
    
    def get_document_analysis_prompt(self) -> str:
        """获取文档分析提示词"""
        return self.document_builder.build_document_analysis_prompt()
    
    def get_script_development_prompt(self, task_target: str, task_prompt: str, mode: str) -> str:
        """获取脚本开发提示词"""
        return self.document_builder.build_script_development_prompt(task_target, task_prompt, mode)
    
    def get_documentation_prompt(self, task_target: str) -> str:
        """获取文档编写提示词"""
        return self.document_builder.build_documentation_prompt(task_target)
    
    def get_error_handling_prompt(self, error_message: str) -> str:
        """获取错误处理提示词"""
        return self.document_builder.build_error_handling_prompt(error_message)
    
    # ==================== 工具方法 ====================
    
    def format_prompt_with_context(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """
        使用上下文信息格式化提示词
        
        Args:
            base_prompt: 基础提示词模板
            context: 上下文信息字典
        """
        try:
            return base_prompt.format(**context)
        except KeyError as e:
            print(f"警告：提示词格式化时缺少上下文信息：{e}")
            return base_prompt
