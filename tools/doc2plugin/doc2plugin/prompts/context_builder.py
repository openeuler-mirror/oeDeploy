"""
上下文构建器 - 负责构建文件生成时所需的各种上下文信息

本模块专注于构建提示词中需要的上下文部分，如文件清单、已生成文件列表、目录树等。
"""

import os
import json
from typing import Dict, List, Optional

from doc2plugin.prompts.constants import ContextPrompts


class ContextBuilder:
    """上下文构建器 - 为文件生成任务构建上下文信息"""
    
    def __init__(self, project_path: str):
        """
        初始化上下文构建器
        
        Args:
            project_path: 项目根目录路径
        """
        self.project_path = project_path
    
    def build_manifest_context(self, file_manifest: Dict, output_files: List[str]) -> str:
        """
        构建文件清单上下文
        
        Args:
            file_manifest: 文件清单字典
            output_files: 当前需要生成的文件列表
            
        Returns:
            文件清单上下文字符串
        """
        context = "\n" + "="*80 + "\n"
        context += ContextPrompts.MANIFEST_CONSTRAINT + "\n\n"
        
        # 添加目录树
        context += ContextPrompts.DIRECTORY_TREE_HEADER
        context += self._build_directory_tree(file_manifest) + "\n"
        
        # 添加文件清单详情
        context += ContextPrompts.MANIFEST_DETAILS_HEADER
        context += self._format_manifest_details(file_manifest) + "\n"
        
        return context
    
    def build_generated_files_context(self, generated_files: List[str]) -> str:
        """
        构建已生成文件上下文
        
        Args:
            generated_files: 已生成的文件路径列表
            
        Returns:
            已生成文件上下文字符串
        """
        if not generated_files:
            return ""
        
        context = ContextPrompts.GENERATED_FILES_HEADER.format(count=len(generated_files))
        
        for i, file_path in enumerate(generated_files):
            full_path = os.path.join(self.project_path, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    context += f"\n### {file_path}\n```\n{content}\n```\n"
                    # 在文件之间添加分隔符（最后一个文件除外）
                    if i < len(generated_files) - 1:
                        context += "=" * 60 + "\n"
                except Exception:
                    context += f"\n### {file_path}\n无法读取文件内容\n"
                    if i < len(generated_files) - 1:
                        context += "=" * 60 + "\n"
        
        context += ContextPrompts.COMPATIBILITY_CHECK
        
        return context
    
    def _build_directory_tree(self, file_manifest: Dict) -> str:
        """构建目录树字符串"""
        files = file_manifest.get('files', [])
        if not files:
            return "(空)"
        
        tree_dict = {}
        for file_info in files:
            path = file_info.get('path', '')
            parts = path.split('/')
            current = tree_dict
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        return self._format_tree(tree_dict)
    
    def _format_tree(self, tree: Dict, prefix: str = "", is_last: bool = True) -> str:
        """递归格式化目录树"""
        lines = []
        items = list(tree.items())
        
        for i, (name, subtree) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            connector = "└── " if is_last_item else "├── "
            lines.append(f"{prefix}{connector}{name}")
            
            if subtree:
                extension = "    " if is_last_item else "│   "
                lines.append(self._format_tree(subtree, prefix + extension, is_last_item))
        
        return "\n".join(lines)
    
    def _format_manifest_details(self, file_manifest: Dict) -> str:
        """格式化文件清单详情"""
        files = file_manifest.get('files', [])
        if not files:
            return "(无文件)"
        
        details = []
        for i, file_info in enumerate(files, 1):
            path = file_info.get('path', '')
            description = file_info.get('description', '')
            depends_on = file_info.get('depends_on', [])
            implementation = file_info.get('implementation', {})
            
            details.append(f"{i}. **{path}**")
            details.append(f"   - 描述: {description}")
            
            if depends_on:
                details.append(f"   - 依赖文件: {', '.join(depends_on)}")
            
            if implementation:
                details.append("   - 实现方案:")
                details.append(f"     * 作用: {implementation.get('purpose', '')}")
                
                params = implementation.get('parameters', [])
                if params:
                    details.append(f"     * 参数: {', '.join(params)}")
                
                refs = implementation.get('referenced_files', [])
                if refs:
                    details.append(f"     * 引用文件: {', '.join(refs)}")
                
                steps = implementation.get('steps', [])
                if steps:
                    details.append("     * 实现步骤:")
                    for step in steps:
                        details.append(f"       - {step}")
                
                notes = implementation.get('notes', [])
                if notes:
                    details.append("     * 注意事项:")
                    for note in notes:
                        details.append(f"       - {note}")
            
            details.append("")
        
        return "\n".join(details)
