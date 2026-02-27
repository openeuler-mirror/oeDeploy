"""目录操作工具 - 提供目录的创建删除等操作"""

import os
import shutil
from typing import Type
from langchain.tools import BaseTool
from pydantic import BaseModel

from doc2plugin.tools.base_tool import DirectoryCreateInput, DirectoryDeleteInput


class DirectoryCreateTool(BaseTool):
    """目录创建工具 - 创建目录（支持递归创建）"""
    
    name: str = "directory_create"
    description: str = "创建目录，支持递归创建多级目录"
    args_schema: Type[BaseModel] = DirectoryCreateInput
    project_path: str
    
    def __init__(self, project_path: str):
        super().__init__(project_path=project_path)
    
    def _run(self, directory_path: str) -> str:
        """执行目录创建"""
        try:
            full_path = os.path.join(self.project_path, directory_path)
            
            if os.path.exists(full_path):
                if os.path.isdir(full_path):
                    return f"目录 {directory_path} 已存在"
                else:
                    return f"错误：{directory_path} 已存在且不是目录"
            
            os.makedirs(full_path)
            return f"成功创建目录 {directory_path}"
            
        except Exception as e:
            return f"创建目录时发生错误：{str(e)}"


class DirectoryDeleteTool(BaseTool):
    """目录删除工具 - 删除目录及其所有内容"""
    
    name: str = "directory_delete"
    description: str = "删除目录及其所有内容"
    args_schema: Type[BaseModel] = DirectoryDeleteInput
    project_path: str
    
    def __init__(self, project_path: str):
        super().__init__(project_path=project_path)
    
    def _run(self, directory_path: str) -> str:
        """执行目录删除"""
        try:
            full_path = os.path.join(self.project_path, directory_path)
            if not os.path.exists(full_path):
                return f"错误：目录 {directory_path} 不存在"
            
            if not os.path.isdir(full_path):
                return f"错误：{directory_path} 不是一个目录"
            
            shutil.rmtree(full_path)
            return f"成功删除目录 {directory_path}"
            
        except Exception as e:
            return f"删除目录时发生错误：{str(e)}"
