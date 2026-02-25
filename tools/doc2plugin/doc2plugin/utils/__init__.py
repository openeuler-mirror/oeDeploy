"""通用工具模块

提供终端输出、LLM客户端、日志管理等通用工具。
"""

from doc2plugin.utils.terminal_output import terminal
from doc2plugin.utils.agent_logger import (
    setup_agent_logger,
    get_agent_logger
)

__all__ = [
    'terminal',
    'setup_agent_logger',
    'get_agent_logger'
]
