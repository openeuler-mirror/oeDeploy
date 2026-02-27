"""工具注册表 - 管理所有可用工具的注册和获取"""

from typing import List
from langchain.tools import BaseTool

from doc2plugin.tools.file_tools import FileListTool, FileReadTool, FileWriteTool, FileDeleteTool
from doc2plugin.tools.directory_tools import DirectoryCreateTool, DirectoryDeleteTool


def get_all_tools(project_path: str) -> List[BaseTool]:
    """
    获取所有可用的工具列表
    
    Args:
        project_path: 项目根目录路径
        
    Returns:
        工具列表，可直接传递给LangChain Agent
        
    设计原则：
        - 只提供通用的文件系统操作工具
        - 不包含任何模式特定的工具
        - LLM 根据开发文档自主决定如何使用这些工具
    """
    return [
        FileListTool(project_path),
        FileReadTool(project_path),
        FileWriteTool(project_path),
        FileDeleteTool(project_path),
        DirectoryCreateTool(project_path),
        DirectoryDeleteTool(project_path),
    ]
