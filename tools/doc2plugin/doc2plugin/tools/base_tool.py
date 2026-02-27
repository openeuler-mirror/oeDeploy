"""基础工具类 - 提供工具的基础功能和输入参数定义"""

from pydantic import BaseModel, Field


class FileListInput(BaseModel):
    """文件列表获取工具的输入参数"""
    directory_path: str = Field(description="要列出文件的目录路径，相对于项目根目录")


class FileReadInput(BaseModel):
    """文件读取工具的输入参数"""
    file_path: str = Field(description="要读取的文件路径，相对于项目根目录")


class FileWriteInput(BaseModel):
    """文件写入工具的输入参数"""
    file_path: str = Field(description="要写入的文件路径，相对于项目根目录")
    content: str = Field(description="要写入的文件内容")


class FileDeleteInput(BaseModel):
    """文件删除工具的输入参数"""
    file_path: str = Field(description="要删除的文件路径，相对于项目根目录")


class DirectoryCreateInput(BaseModel):
    """目录创建工具的输入参数"""
    directory_path: str = Field(description="要创建的目录路径，相对于项目根目录")


class DirectoryDeleteInput(BaseModel):
    """目录删除工具的输入参数"""
    directory_path: str = Field(description="要删除的目录路径，相对于项目根目录")
