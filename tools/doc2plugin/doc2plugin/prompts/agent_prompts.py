"""
Agent执行时使用的提示词模板

本模块提供Agent在执行具体任务时与LLM交互的提示词。
经过重构，现在职责更加清晰，代码更易维护。
"""

from doc2plugin.prompts.file_generation_prompts import FileGenerationPromptBuilder
from doc2plugin.prompts.context_builder import ContextBuilder


class AgentPromptTemplates:
    """Agent执行提示词模板 - 主入口类"""
    
    def __init__(self, project_path: str = None):
        """
        初始化Agent提示词模板
        
        Args:
            project_path: 项目路径（可选，用于上下文构建）
        """
        self.project_path = project_path
        self.file_gen_builder = FileGenerationPromptBuilder()
        self.context_builder = ContextBuilder(project_path) if project_path else None
    
    # ==================== 文件清单相关 ====================
    
    @staticmethod
    def get_file_manifest_task_prompt(target: str, prompt_constraint: str) -> str:
        """获取文件清单生成任务的提示词"""
        return FileGenerationPromptBuilder.build_manifest_task_prompt(target, prompt_constraint)
    
    @staticmethod
    def get_file_manifest_analysis_prompt(prompt: str, content: str) -> str:
        """获取文件清单分析任务的完整提示词"""
        return FileGenerationPromptBuilder.build_manifest_analysis_prompt(prompt, content)
    
    # ==================== 文件生成相关 ====================
    
    @staticmethod
    def get_file_generation_prompt(target: str, prompt_constraint: str, description: str) -> str:
        """获取文件生成任务的提示词"""
        return FileGenerationPromptBuilder.build_file_generation_prompt(
            target, prompt_constraint, description
        )
    
    # ==================== 测试相关 ====================
    
    @staticmethod
    def get_test_script_generation_requirements() -> str:
        """获取测试脚本生成的要求"""
        return FileGenerationPromptBuilder.build_test_script_prompt()
    
    # ==================== 修改相关 ====================
    
    @staticmethod
    def get_modification_requirements() -> str:
        """获取修改清单的生成要求"""
        return FileGenerationPromptBuilder.build_modification_requirements()
    
    # ==================== 上下文构建相关 ====================
    @staticmethod
    def get_directory_tree_prompt() -> str:
        """获取目录树展示的提示"""
        from doc2plugin.prompts.constants import ContextPrompts
        return ContextPrompts.DIRECTORY_TREE_HEADER
    
    @staticmethod
    def get_file_manifest_details_header() -> str:
        """获取文件清单详情的头部"""
        from doc2plugin.prompts.constants import ContextPrompts
        return ContextPrompts.MANIFEST_DETAILS_HEADER
    
    @staticmethod
    def get_generated_files_context_header(file_count: int) -> str:
        """获取已生成文件上下文的头部"""
        from doc2plugin.prompts.constants import ContextPrompts
        return ContextPrompts.GENERATED_FILES_HEADER.format(count=file_count)
    
    @staticmethod
    def get_compatibility_check_prompt() -> str:
        """获取兼容性检查的提示"""
        from doc2plugin.prompts.constants import ContextPrompts
        return ContextPrompts.COMPATIBILITY_CHECK
    
    # ==================== 占位符和警告相关 ====================
    
    @staticmethod
    def get_document_refinement_placeholder() -> str:
        """获取文档提纯的占位符内容"""
        return FileGenerationPromptBuilder.get_document_refinement_placeholder()
    
    @staticmethod
    def get_no_doc_warning() -> str:
        """获取无文档警告信息"""
        return FileGenerationPromptBuilder.get_no_doc_warning()
    
    @staticmethod
    def get_yaml_syntax_warning() -> str:
        """获取YAML/Ansible语法警告"""
        return FileGenerationPromptBuilder.get_yaml_syntax_warning()
