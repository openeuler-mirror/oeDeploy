"""
统一的Agent日志管理模块

本模块提供全局的日志记录器，用于记录agent.log。
该日志记录除了LLM交互(llm.log)和终端输出以外的所有日志信息。
"""

import os
import logging
from typing import Optional


class AgentLogger:
    """
    Agent日志管理器
    
    提供统一的日志记录接口，所有模块共享同一个日志记录器。
    """
    
    _instance: Optional[logging.Logger] = None
    _current_project_path: Optional[str] = None
    
    @classmethod
    def setup(cls, project_path: str) -> logging.Logger:
        """
        设置日志记录器
        
        Args:
            project_path: 项目路径，用于确定日志文件位置
            
        Returns:
            配置好的日志记录器
            
        Raises:
            RuntimeError: 如果日志记录器初始化失败
        """
        # 如果已经为同一项目设置过，直接返回
        if cls._instance is not None and cls._current_project_path == project_path:
            return cls._instance
        
        try:
            # 清理旧的处理器
            if cls._instance is not None:
                for handler in cls._instance.handlers[:]:
                    handler.close()
                    cls._instance.removeHandler(handler)
            
            # 创建或获取logger
            logger = logging.getLogger('doc2plugin.agent')
            logger.setLevel(logging.INFO)
            logger.handlers.clear()
            logger.propagate = False
            
            # 创建日志目录
            log_dir = os.path.join(project_path, 'cache')
            os.makedirs(log_dir, exist_ok=True)
            
            # 创建文件处理器
            file_handler = logging.FileHandler(
                os.path.join(log_dir, 'agent.log'),
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            
            # 设置格式化器
            formatter = logging.Formatter(
                '[%(asctime)s - %(name)s - %(levelname)s] %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            
            cls._instance = logger
            cls._current_project_path = project_path
            
            return logger
        except Exception as e:
            raise RuntimeError(f"初始化agent日志记录器失败: {e}")
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        获取日志记录器
        
        Returns:
            日志记录器
            
        Raises:
            RuntimeError: 如果日志记录器未初始化
        """
        if cls._instance is None:
            raise RuntimeError("agent日志记录器未初始化，请先调用setup()")
        return cls._instance


# 便捷函数
def setup_agent_logger(project_path: str) -> logging.Logger:
    """
    设置agent日志记录器
    
    Args:
        project_path: 项目路径
        
    Returns:
        配置好的日志记录器
    """
    return AgentLogger.setup(project_path)


def get_agent_logger() -> logging.Logger:
    """
    获取agent日志记录器
    
    Returns:
        日志记录器
        
    Raises:
        RuntimeError: 如果日志记录器未初始化
    """
    return AgentLogger.get_logger()
