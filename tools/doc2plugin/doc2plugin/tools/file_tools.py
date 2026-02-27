"""文件操作工具 - 提供文件的读写删除等操作"""

import os
from typing import Type
from langchain.tools import BaseTool
from pydantic import BaseModel

from doc2plugin.tools.base_tool import FileListInput, FileReadInput, FileWriteInput, FileDeleteInput


class FileListTool(BaseTool):
    """文件列表获取工具 - 获取指定目录下的文件和子目录列表"""
    
    name: str = "file_list"
    description: str = "获取指定目录下的文件和子目录列表"
    args_schema: Type[BaseModel] = FileListInput
    project_path: str
    
    def __init__(self, project_path: str):
        super().__init__(project_path=project_path)
    
    def _run(self, directory_path: str) -> str:
        """执行文件列表获取"""
        try:
            full_path = os.path.join(self.project_path, directory_path)
            if not os.path.exists(full_path):
                return f"错误：目录 {directory_path} 不存在"
            
            if not os.path.isdir(full_path):
                return f"错误：{directory_path} 不是一个目录"
            
            items = []
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                if os.path.isdir(item_path):
                    items.append(f"[目录] {item}/")
                else:
                    items.append(f"[文件] {item}")
            
            if not items:
                return f"目录 {directory_path} 为空"
            
            return f"目录 {directory_path} 的内容：\n" + "\n".join(items)
            
        except Exception as e:
            return f"获取文件列表时发生错误：{str(e)}"


class FileReadTool(BaseTool):
    """文件读取工具 - 读取指定文件的内容"""
    
    name: str = "file_read"
    description: str = "读取指定文件的内容"
    args_schema: Type[BaseModel] = FileReadInput
    project_path: str
    
    def __init__(self, project_path: str):
        super().__init__(project_path=project_path)
    
    def _run(self, file_path: str) -> str:
        """执行文件读取"""
        try:
            full_path = os.path.join(self.project_path, file_path)
            if not os.path.exists(full_path):
                return f"错误：文件 {file_path} 不存在"
            
            if not os.path.isfile(full_path):
                return f"错误：{file_path} 不是一个文件"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"文件 {file_path} 的内容：\n{content}"
            
        except UnicodeDecodeError:
            return f"错误：文件 {file_path} 不是文本文件或编码不支持"
        except Exception as e:
            return f"读取文件时发生错误：{str(e)}"


class FileWriteTool(BaseTool):
    """文件写入工具 - 创建或覆盖写入文件内容"""
    
    name: str = "file_write"
    description: str = "创建或覆盖写入文件内容"
    args_schema: Type[BaseModel] = FileWriteInput
    project_path: str
    
    def __init__(self, project_path: str):
        super().__init__(project_path=project_path)
    
    def _run(self, file_path: str, content: str) -> str:
        """执行文件写入"""
        try:
            full_path = os.path.join(self.project_path, file_path)
            
            # 确保父目录存在
            parent_dir = os.path.dirname(full_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"成功写入文件 {file_path}"
            
        except Exception as e:
            return f"写入文件时发生错误：{str(e)}"


class FileDeleteTool(BaseTool):
    """文件删除工具 - 删除指定文件"""
    
    name: str = "file_delete"
    description: str = "删除指定文件"
    args_schema: Type[BaseModel] = FileDeleteInput
    project_path: str
    
    def __init__(self, project_path: str):
        super().__init__(project_path=project_path)
    
    def _run(self, file_path: str) -> str:
        """执行文件删除"""
        try:
            full_path = os.path.join(self.project_path, file_path)
            if not os.path.exists(full_path):
                return f"错误：文件 {file_path} 不存在"
            
            if not os.path.isfile(full_path):
                return f"错误：{file_path} 不是一个文件"
            
            os.remove(full_path)
            return f"成功删除文件 {file_path}"
            
        except Exception as e:
            return f"删除文件时发生错误：{str(e)}"
