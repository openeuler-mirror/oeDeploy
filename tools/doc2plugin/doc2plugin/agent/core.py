"""
AI Agent核心逻辑 - 基于LangChain和LangGraph

本模块实现了doc2plugin的核心AI Agent，充分利用LangChain框架的能力：
- 使用 LangGraph 进行工作流编排
- 使用 ChatPromptTemplate 管理提示词
- 使用 OutputParsers 解析输出
- 使用 Callbacks 进行日志记录
"""

import os
from typing import Dict, Any

from langchain_openai import ChatOpenAI

from doc2plugin.tools import get_all_tools
from doc2plugin.prompts import PromptManager
from doc2plugin.utils.terminal_output import terminal
from doc2plugin.config_manager import ConfigManager
from doc2plugin.utils.llm_client import LLMClient, setup_llm_logger
from doc2plugin.utils.agent_logger import get_agent_logger
from doc2plugin.agent.langgraph_workflow import LangGraphWorkflowManager


class Doc2PluginAgent:
    """
    Doc2Plugin AI Agent - 基于 LangChain 和 LangGraph 的智能代码编写代理
    
    1. LangGraph 状态图管理工作流
    2. ChatPromptTemplate 管理提示词
    3. OutputParsers 解析输出
    4. Callbacks 进行日志记录和统计
    5. with_retry 自动重试
    """
    
    def __init__(self, project_path: str, action: str = 'compose'):
        """
        初始化AI Agent
        
        Args:
            project_path: 项目根目录路径
            action: 操作类型，如 'compose', 'test', 'modify'
        """
        self.project_path = project_path
        self.action = action
        self.config = None
        self.llm = None
        self.llm_client = None
        self.tools = None
        self.prompts = None
        self.workflow_manager = None
        # 获取agent日志记录器（已在命令模块中设置）
        self.logger = get_agent_logger()
        # 设置LLM专用日志记录器
        self.llm_logger = self._setup_llm_logger()
        # 初始化配置管理器
        self.config_manager = ConfigManager(project_path, self.logger)
    
    def _setup_llm_logger(self):
        """设置LLM专用日志记录器"""
        log_dir = os.path.join(self.project_path, 'cache')
        os.makedirs(log_dir, exist_ok=True)
        return setup_llm_logger(log_dir)
    
    def load_config(self) -> bool:
        """
        加载项目配置文件 (work.yaml)
        
        Returns:
            bool: 加载成功返回True，失败返回False
        """
        # 使用配置管理器加载配置，传入当前操作类型
        if not self.config_manager.load_config(self.action):
            return False
        
        self.config = self.config_manager.get_raw_config()
        
        # 验证关键配置项
        if not self.config_manager.validate_api_key():
            self.logger.error("API 密钥无效或为默认值")
            return False
        if not self.config_manager.validate_task_target():
            self.logger.error("任务目标无效或为默认值")
            return False
        
        # 初始化提示词管理器
        develop_doc_content = self.config_manager.get_develop_doc_content()
        mode_prompt = self.config_manager.get_mode_prompt()
        self.prompts = PromptManager(develop_doc_content, mode_prompt)
        
        if develop_doc_content:
            doc_length = len(develop_doc_content)
            self.logger.info(f"提示词管理器初始化完成（文档驱动模式，文档总长度: {doc_length} 字符）")
        else:
            self.logger.info("提示词管理器初始化完成（非文档驱动模式）")
        
        self.logger.info("配置文件加载成功")
        return True
    
    def initialize_llm(self) -> bool:
        """
        初始化LLM (Large Language Model)
        
        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        llm_config = self.config_manager.get_llm_config()
        if not llm_config:
            self.logger.error("请先加载配置文件")
            return False
        
        try:
            # 构建LLM参数
            llm_params = {
                'base_url': llm_config.base_url,
                'api_key': llm_config.api_key,
                'model': llm_config.model_name,
                'timeout': llm_config.timeout,
                'temperature': llm_config.temperature,
                'streaming': True,  # 启用流式输出
            }
            
            # 只有在max_tokens不为None时才添加该参数
            if llm_config.max_tokens is not None:
                llm_params['max_tokens'] = llm_config.max_tokens
            
            self.llm = ChatOpenAI(**llm_params)
            
            # 初始化LLM客户端（使用with_retry）
            self.llm_client = LLMClient(
                llm=self.llm,
                logger=self.logger,
                llm_logger=self.llm_logger,
                max_retries=llm_config.max_llm_retries,
                retry_delay=llm_config.llm_retry_delay
            )
            
            self.logger.info("LLM客户端初始化成功")
            token_info = f"无限制" if llm_config.max_tokens is None else f"{llm_config.max_tokens}"
            self.logger.info(f"LLM初始化成功: {llm_config.model_name} (max_tokens: {token_info})")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化LLM时发生错误: {e}")
            return False
    
    def initialize_tools(self) -> bool:
        """
        初始化工具集
        
        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        if not self.llm:
            self.logger.error("请先初始化LLM")
            return False
        
        try:
            # 获取工具列表
            self.tools = get_all_tools(self.project_path)
            
            # 初始化基于 LangGraph 的工作流管理器
            self.workflow_manager = LangGraphWorkflowManager(
                project_path=self.project_path,
                llm_client=self.llm_client,
                tools=self.tools,
                prompts=self.prompts,
                config_manager=self.config_manager,
                logger=self.logger
            )
            
            self.logger.info("工具集和LangGraph工作流管理器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化工具集时发生错误: {e}")
            return False
    
    def execute_workflow(self) -> bool:
        """
        执行工作流程 - 使用 LangGraph 状态图进行任务编排
        
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        terminal.info("开始代码编写流程", 'process')
        self.logger.info("开始执行代码编写流程（基于LangGraph）")
        
        try:
            # 使用 LangGraph 执行整个工作流
            # 工作流包括：文档提纯 -> 生成文件清单 -> 生成任务 -> 执行任务 -> 验证
            success = self.workflow_manager.execute_workflow()
            
            if success:
                terminal.success("工作流程执行完成！", 'check')
                self.logger.info("工作流程执行完成")
                return True
            else:
                terminal.error("工作流程执行失败")
                self.logger.error("工作流程执行失败")
                return False
                
        except Exception as e:
            terminal.error(f"工作流程执行时发生错误: {e}")
            self.logger.error(f"工作流程执行时发生错误: {e}")
            return False
    
    def execute_test_workflow(self) -> bool:
        """
        执行测试工作流程 - 生成测试脚本
        
        test.sh和test.log如果同时存在，则跳过生成测试脚本，从而支持测试与修改交替进行。
        
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        self.logger.info("开始执行测试脚本生成流程")
        
        try:
            # 使用 workflow_manager 执行测试脚本生成
            success = self.workflow_manager.execute_test_workflow()
            
            if success:
                terminal.success("测试脚本生成完成！", 'check')
                self.logger.info("测试脚本生成完成")
                return True
            else:
                terminal.error("测试脚本生成失败")
                self.logger.error("测试脚本生成失败")
                return False
                
        except Exception as e:
            terminal.error(f"测试脚本生成时发生错误: {e}")
            self.logger.error(f"测试脚本生成时发生错误: {e}")
            return False
    
    def execute_modify_workflow(self) -> bool:
        """
        执行修改工作流程 - 基于测试结果修改代码
        
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        self.logger.info("开始执行代码修改流程")
        
        try:
            # 使用 workflow_manager 执行修改流程
            success = self.workflow_manager.execute_modify_workflow()
            
            if success:
                terminal.success("代码修改完成！", 'check')
                self.logger.info("代码修改完成")
                return True
            else:
                terminal.error("代码修改失败")
                self.logger.error("代码修改失败")
                return False
                
        except Exception as e:
            terminal.error(f"代码修改时发生错误: {e}")
            self.logger.error(f"代码修改时发生错误: {e}")
            return False
    
    def get_project_status(self) -> Dict[str, Any]:
        """
        获取项目状态信息
        
        Returns:
            Dict: 包含项目状态的字典
        """
        status = {
            'project_path': self.project_path,
            'config_loaded': self.config is not None,
            'llm_initialized': self.llm is not None,
            'tools_initialized': self.tools is not None,
        }
        
        if self.config_manager:
            task_config = self.config_manager.get_task_config()
            llm_config = self.config_manager.get_llm_config()
            if task_config:
                status['task_target'] = task_config.target
                status['mode'] = task_config.mode.value
            if llm_config:
                status['model_name'] = llm_config.model_name
        
        return status
