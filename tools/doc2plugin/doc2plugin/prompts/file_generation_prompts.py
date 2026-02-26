"""
文件生成提示词构建器 - 专门负责构建文件生成相关的提示词

本模块包含文件清单生成、单个文件生成、测试脚本生成等提示词的构建逻辑。
"""

from typing import Dict

from doc2plugin.prompts.constants import (
    OutputFormat,
    FileManifestFormat,
    PlaceholderContent
)


class FileGenerationPromptBuilder:
    """文件生成提示词构建器"""
    
    @staticmethod
    def build_manifest_task_prompt(target: str, constraint: str) -> str:
        """
        构建文件清单生成任务的提示词
        
        Args:
            target: 用户目标
            constraint: 环境约束
            
        Returns:
            完整的提示词
        """
        return f"""
请根据用户需求、提纯后的文档（cache/source.md）和开发文档，规划项目的文件结构，输出完整的文件清单。

用户目标：{target}

环境约束：{constraint}

请分析以上需求，规划需要生成哪些文件。

**重要：每个文件必须包含详细的implementation字段**，包含以下5个子字段：
{FileManifestFormat.IMPLEMENTATION_FIELDS}"""
    
    @staticmethod
    def build_manifest_analysis_prompt(base_prompt: str, content: str) -> str:
        """
        构建文件清单分析任务的完整提示词
        
        Args:
            base_prompt: 基础提示词
            content: 文档内容
            
        Returns:
            完整的分析提示词
        """
        return f"""{base_prompt}

================================================================================
分析内容:
================================================================================

{content}

================================================================================
{OutputFormat.JSON_PURE}

{FileManifestFormat.FILE_MANIFEST_REQUIREMENTS}

{FileManifestFormat.JSON_SCHEMA}

{FileManifestFormat.REQUIREMENTS}"""
    
    @staticmethod
    def build_file_generation_prompt(target: str, constraint: str, description: str) -> str:
        """
        构建单个文件生成任务的提示词
        
        Args:
            target: 用户目标
            constraint: 环境约束
            description: 文件说明
            
        Returns:
            文件生成提示词
        """
        return f"""
根据用户需求、提纯后的文档（cache/source.md）、开发文档、文件清单和已生成的文件，生成新文件

用户目标：{target}

环境约束：{constraint}

文件说明：{description}

要求：
- 请确保新文件与已生成的文件完全兼容，特别是文件引用、配置项、变量名等必须保持一致。
- 请确保新文件与已规划的文件完全兼容，尤其不能引用不存在的文件。"""
    
    @staticmethod
    def build_test_script_prompt() -> str:
        """
        构建测试脚本生成提示词
        
        Returns:
            测试脚本生成要求
        """
        return "="*80 + "\n# 任务要求\n" + "="*80 + "\n" + """
请根据以上信息，生成一个测试脚本cache/test.sh，用于测试已经开发好的代码。

测试脚本要求：
1. 测试脚本必须覆盖已开发代码的主要功能
2. 可以分成几个步骤，每个步骤单独判断执行效果
3. 所有步骤必须在测试脚本中一次性执行完
4. 测试脚本全部执行成功返回0，否则返回非0值
5. 关键命令行的返回值、stdout、stderr需要输出到日志文件cache/test.log
6. 测试脚本必须是可重入的，确保无论何时中断执行，都不影响重复测试的结果
7. 测试脚本必须是bash脚本，以#!/bin/bash开头

**重要：请以JSON格式返回，格式如下：**
{"script_content": "实际的bash脚本内容"}

只返回纯JSON，不要添加任何解释。
"""
    
    @staticmethod
    def build_modification_requirements() -> str:
        """
        构建修改清单的生成要求
        
        Returns:
            修改清单生成要求
        """
        return """

# 修改清单生成要求

请根据测试结果分析问题，并生成修改清单。修改清单必须是纯JSON格式，包含以下结构：

```json
{
  "analysis": "对测试失败原因的分析总结（1-3句话）",
  "operations": [
    {
      "action": "create|modify|delete",
      "type": "file|directory",
      "path": "相对于项目根目录的路径",
      "description": "该文件的作用和需要修改的内容（详细说明，用于后续LLM生成文件内容）",
      "reason": "为什么需要这个修改"
    }
  ]
}
```

字段说明：
- `analysis`: 简要分析测试失败的根本原因
- `operations`: 操作列表，按执行顺序排列
  - `action`: 操作类型（create=新增, modify=修改, delete=删除）
  - `type`: 目标类型（file=文件, directory=目录）
  - `path`: 文件或目录路径（相对于项目根目录）
  - `description`: 该文件的作用和需要修改的内容（详细说明）
  - `reason`: 为什么需要这个修改

注意事项：
1. 只输出纯JSON，不要包含任何其他文字说明
2. **不要在operations中包含content字段**，文件内容会在后续步骤中单独生成
3. description字段要详细说明该文件需要做什么修改，这些信息将用于指导后续的文件生成
4. 如果测试已通过或无需修改，operations数组可以为空
5. 修改时要考虑文件之间的依赖关系
6. 确保修改后的代码符合开发文档的规范
7. 优先修改代码而非测试脚本，除非测试脚本本身有明显错误

请输出修改清单（纯JSON格式）："""
    
    @staticmethod
    def get_yaml_syntax_warning() -> str:
        """获取YAML/Ansible语法警告"""
        return OutputFormat.YAML_JINJA2_WARNING
    
    @staticmethod
    def get_document_refinement_placeholder() -> str:
        """获取文档提纯的占位符内容"""
        return PlaceholderContent.NO_DOC_PLACEHOLDER
    
    @staticmethod
    def get_no_doc_warning() -> str:
        """获取无文档警告信息"""
        return PlaceholderContent.NO_DOC_WARNING
