"""
文档处理提示词构建器 - 构建文档提取、分析等相关的提示词

文档提示词用于指导AI Agent进行文档分析、提取、生成等操作。
"""

from doc2plugin.prompts.components import PromptComponents, PromptConfig


class DocumentPromptBuilder:
    """文档提示词构建器"""
    
    def __init__(self):
        """初始化文档提示词构建器"""
        self.components = PromptComponents()
        self.config = PromptConfig()
    
    def build_document_refinement_prompt(self, task_target: str, task_prompt: str) -> str:
        """
        构建文档提纯提示词 - 根据任务目标提炼doc/目录下的文档
        
        Args:
            task_target: 任务目标描述
            task_prompt: 环境约束和技术要求
        """
        return f"""
请根据任务目标，分析doc/目录下的所有文档，提炼出与任务相关的关键信息。

任务目标：{task_target}

环境约束：{task_prompt}

**提纯要求**：
1. 仔细阅读doc/目录下的所有文档
2. 根据任务目标，提取与任务直接相关的信息
3. 过滤掉与任务无关的干扰信息（如营销内容、无关功能说明、过于详细的理论等）
4. 将提炼的信息整理成结构化的markdown格式
5. 确保提炼后的文档清晰、准确、完整，便于后续任务使用

你需要关注以下内容：
1. 软件的基本信息（名称、版本、依赖等）
2. 安装前的环境准备和系统要求
3. 详细的安装步骤和命令
4. 配置文件的位置和关键配置项
5. 服务启动和停止的方法
6. 卸载或清理的步骤
7. 常见问题和故障排除

请忽略以下内容：（原始文本可能是来自网页的html文本，包含大量干扰信息）
- 与部署无关的功能介绍
- 与当前任务目标无关的内容
- 过于详细的理论说明
- 营销性质的描述和链接

**输出要求**：
- 直接输出markdown格式的文档内容
- 不要使用代码块标记（```markdown）
- 内容应该结构清晰，便于后续任务使用
- 确保所有关键信息都已包含，但去除干扰内容
"""
    
    def build_document_analysis_prompt(self) -> str:
        """构建文档分析提示词 - 用于分析任务的通用提示词"""
        return f"""请分析提供的文档内容，理解其中的关键信息和部署要求。

{self.components.get_document_analysis_focus()}

请提供结构化的分析结果，为后续任务提供清晰的信息基础。"""
    
    def build_script_development_prompt(self, task_target: str, task_prompt: str, mode: str) -> str:
        """
        构建脚本开发提示词 - 指导AI开发部署脚本（仅用于 shell 模式）
        
        Args:
            task_target: 用户的目标描述
            task_prompt: 用户的补充提示
            mode: 模式类型
        """
        requirements = self.components.format_requirements_list(self.config.SCRIPT_REQUIREMENTS)
        structure = self.components.format_requirements_list(self.config.SCRIPT_STRUCTURE)
        
        return f"""
请根据cache/source.md中提炼的文档信息，开发一个 shell 部署脚本。

用户需求：{task_target}

环境要求：{task_prompt}

脚本开发要求：
{requirements}

脚本结构建议：
{structure}

**{self.config.DIRECT_OUTPUT_INSTRUCTION.format(content_type='shell脚本代码，以#!/bin/bash开头')}脚本应该可以直接保存为.sh文件并执行。**"""
    
    def build_documentation_prompt(self, task_target: str) -> str:
        """
        构建文档编写提示词 - 指导AI编写用户文档
        
        Args:
            task_target: 用户的目标描述
        """
        requirements = self.components.format_requirements_list(self.config.DOCUMENTATION_REQUIREMENTS)
        
        return f"""
请为开发的部署脚本编写详细的用户文档（readme.md）。

项目目标：{task_target}

文档应该包含以下内容：
1. 项目简介和功能概述
2. 系统要求和环境准备
3. 脚本的详细使用方法
4. 命令行参数说明
5. 配置选项和自定义方法
6. 常见问题和故障排除
7. 注意事项和最佳实践

文档编写要求：
{requirements}

**{self.config.DIRECT_OUTPUT_INSTRUCTION.format(content_type='markdown文档内容，以标题开头')}文档应该可以直接保存为.md文件。**"""
    
    def build_error_handling_prompt(self, error_message: str) -> str:
        """
        构建错误处理提示词 - 指导AI处理执行过程中的错误
        
        Args:
            error_message: 错误信息
        """
        return f"""
在执行任务过程中遇到了以下错误：

错误信息：{error_message}

请分析这个错误的可能原因，并提供解决方案：
1. 分析错误的根本原因
2. 提供具体的解决步骤
3. 如果需要修改代码或配置，请给出具体的修改建议
4. 提供预防类似错误的建议

请以专业和建设性的方式提供帮助。"""
