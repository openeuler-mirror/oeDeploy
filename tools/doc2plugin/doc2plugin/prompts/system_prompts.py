"""
系统提示词构建器 - 构建系统级别的提示词

系统提示词定义了AI Agent的角色、能力范围和行为准则。
"""

from typing import Optional, List
from doc2plugin.prompts.components import PromptComponents


class SystemPromptBuilder:
    """系统提示词构建器"""
    
    def __init__(self, develop_doc_content: Optional[str] = None, mode_prompt: Optional[List[str]] = None):
        """
        初始化系统提示词构建器
        
        Args:
            develop_doc_content: 开发文档内容（用于文档驱动模式）
            mode_prompt: 模式专用提示词列表（高优先级）
        """
        self.develop_doc_content = develop_doc_content
        self.mode_prompt = mode_prompt or []
        self.components = PromptComponents()
    
    def build_system_prompt(self, mode: str = "shell") -> str:
        """
        构建系统提示词
        
        Args:
            mode: 模式类型（shell 或其他文档驱动的模式）
            
        Returns:
            完整的系统提示词
        """
        if mode == "shell":
            return self._build_shell_mode_prompt()
        else:
            return self._build_doc_driven_prompt(mode)
    
    def _build_shell_mode_prompt(self) -> str:
        """构建shell模式的系统提示词"""
        base_prompt = f"""
你是一个专业的软件部署脚本开发助手，专门负责根据软件部署文档编写可执行的脚本。

{self.components.get_main_responsibilities()}

{self.components.get_work_principles()}

{self.components.get_available_tools()}

请始终以专业、准确、高效的方式完成任务，并根据实际情况灵活调整工作计划。"""
        
        # 添加模式专用提示词（如果有）
        if self.mode_prompt:
            base_prompt += self._format_mode_prompt_section()
        
        return base_prompt
    
    def _build_doc_driven_prompt(self, mode: str) -> str:
        """
        构建文档驱动模式的系统提示词
        
        Args:
            mode: 模式名称（如 'oedp'）
        """
        if not self.develop_doc_content:
            raise ValueError(
                f"模式 '{mode}' 需要开发文档，但未找到文档内容。\n"
                f"请确保在 modes.yaml 中正确配置了该模式的开发文档路径。"
            )
        
        base_prompt = f"""
你是一个专业的项目开发助手，专门负责根据开发文档编写符合规范的项目代码。

**重要：你必须严格遵循以下开发文档中的所有规范和要求，这是最高优先级！**

**注意：以下可能包含多个开发文档，每个文档都定义了项目开发的重要规范。请综合考虑所有文档的要求。**

==================== 开发文档开始 ====================

{self.develop_doc_content}

==================== 开发文档结束 ====================

{self.components.get_available_tools()}

**请严格遵循上述所有开发文档中的规范、格式要求和最佳实践！**
项目的所有文件结构、命名规范、技术选型都必须完全符合所有文档的要求。
如果多个文档之间存在冲突或差异，请优先遵循更具体、更详细的规范。"""
        
        # 添加模式专用提示词（如果有）
        if self.mode_prompt:
            base_prompt += self._format_mode_prompt_section(highest_priority=True)
        
        return base_prompt
    
    def _format_mode_prompt_section(self, highest_priority: bool = False) -> str:
        """格式化模式专用提示词部分"""
        if not self.mode_prompt:
            return ""
        
        priority_note = "甚至高于上述开发文档：" if highest_priority else ""
        
        section = "\n\n" + "=" * 80 + "\n"
        section += "**【重要】模式专用提示（最高优先级）**\n\n"
        section += f"请务必严格遵守以下提示，这些提示具有最高优先级{priority_note}\n\n"
        for idx, prompt in enumerate(self.mode_prompt, 1):
            section += f"{idx}. {prompt}\n"
        section += "\n" + "=" * 80
        
        return section
