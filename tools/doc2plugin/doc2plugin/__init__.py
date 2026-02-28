"""
doc2plugin: AI Agent工具，智能代码编写助手

基于LangChain开发的智能代码编写工具，能够根据部署文档自动生成可执行的部署脚本。
"""

__version__ = "1.0.0"
__author__ = "doc2plugin"

# 导出主要类和模块
from doc2plugin.agent import Doc2PluginAgent
from doc2plugin.config_manager import ConfigManager, LLMContextConfig, ModeType
from doc2plugin.prompts import PromptManager
from doc2plugin.tools import get_all_tools

__all__ = [
    'Doc2PluginAgent',
    'ConfigManager', 
    'LLMContextConfig',
    'ModeType',
    'PromptManager',
    'get_all_tools'
]
