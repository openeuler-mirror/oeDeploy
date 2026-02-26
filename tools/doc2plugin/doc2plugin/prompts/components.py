"""
提示词组件 - 提供可复用的提示词组件和配置

本模块定义了提示词中使用的通用组件、配置项和格式化函数。
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class PromptConfig:
    """提示词配置类 - 定义常用的格式化指令和要求"""
    
    # 输出格式指令
    DIRECT_OUTPUT_INSTRUCTION = "请直接返回完整的{content_type}内容，不要包含任何markdown代码块标记或解释文字。"
    
    # 文档要求
    DOCUMENTATION_REQUIREMENTS = [
        "使用清晰的markdown格式",
        "提供具体的使用示例", 
        "包含必要的代码块和命令示例",
        "结构清晰，便于用户快速上手",
        "考虑不同技术水平的用户需求"
    ]
    
    # 脚本开发要求
    SCRIPT_REQUIREMENTS = [
        "脚本应该支持install和uninstall两种基本模式",
        "提供清晰的命令行参数和帮助信息",
        "包含完善的错误处理和用户反馈",
        "支持常见配置参数的自定义",
        "具有良好的日志输出和调试信息",
        "遵循shell脚本的最佳实践"
    ]
    
    # 脚本结构建议
    SCRIPT_STRUCTURE = [
        "参数解析和帮助信息",
        "环境检查和依赖验证",
        "安装函数实现",
        "卸载函数实现", 
        "配置管理函数",
        "错误处理和清理函数",
        "主函数和入口逻辑"
    ]
    
    # 质量检查项目
    QUALITY_CHECK_ITEMS = {
        "脚本功能完整性": [
            "是否实现了所有必需的功能",
            "参数处理是否正确",
            "错误处理是否完善"
        ],
        "代码质量": [
            "代码结构是否清晰",
            "变量命名是否规范", 
            "注释是否充分"
        ],
        "安全性": [
            "是否存在安全风险",
            "权限检查是否合适",
            "输入验证是否充分"
        ],
        "用户体验": [
            "帮助信息是否清晰",
            "错误提示是否友好",
            "操作流程是否简单"
        ],
        "文档质量": [
            "文档是否完整",
            "示例是否准确",
            "说明是否清晰"
        ]
    }


class PromptComponents:
    """提示词组件类 - 提供可复用的提示词组件"""
    
    @staticmethod
    def get_work_principles() -> str:
        """获取工作原则描述"""
        return """
工作原则：
- 仔细分析项目现状，制定适合的任务计划
- 优先考虑脚本的安全性、稳定性和可维护性
- 提供清晰的错误处理和用户反馈
- 支持多样化的输出需求（单个/多个文件、不同格式等）
- 编写详细的用户文档说明使用方法
- 具备任务执行的自我验证和纠错能力"""
    
    @staticmethod
    def get_main_responsibilities() -> str:
        """获取主要职责描述"""
        return """
你的主要职责：
1. 分析用户提供的部署文档，理解项目需求和现状
2. 根据用户需求动态设计合理的任务计划（todo list）
3. 使用提供的工具完成各种类型的任务（分析、提取、生成、验证等）
4. 确保生成的脚本和文档具有良好的质量和可用性
5. 支持灵活的输出格式（多个脚本文件、多个文档、目录结构等）"""
    
    @staticmethod
    def get_available_tools() -> str:
        """获取可用工具列表及其使用说明"""
        return """
## 可用工具

你可以使用以下工具来完成任务：

1. **file_list** - 列出目录内容
   - 参数：directory_path (字符串，相对路径)

2. **file_read** - 读取文件内容
   - 参数：file_path (字符串，相对路径)

3. **file_write** - 写入文件内容
   - 参数：file_path (字符串，相对路径), content (字符串)

4. **file_delete** - 删除文件
   - 参数：file_path (字符串，相对路径)

5. **directory_create** - 创建单个目录
   - 参数：directory_path (字符串，相对路径)
   - 注意：每次只能创建一个目录，支持递归创建父目录

6. **directory_delete** - 删除目录
   - 参数：directory_path (字符串，相对路径)
"""
    
    @staticmethod
    def get_task_types_description() -> str:
        """获取任务类型描述"""
        return """
## 任务类型说明

1. **分析任务 (analysis)** - 分析文档、需求等
   - 参数示例：{"prompt": "分析内容", "input_files": ["cache/source.md"], "output_file": "cache/result.md"}

2. **提取任务 (extraction)** - 提取关键信息、内容提炼等
   - 参数示例：{"source": "doc/xxx", "target": "cache/xxx", "extract_fields": [...]}

3. **生成任务 (generation)** - 生成脚本、文档等
   - **重要**：必须返回JSON格式，包含 file_content 字段
   - **路径要求**：output_file 必须以 plugin/ 开头
   - 响应格式：{"file_content": "实际文件内容"}
   - 参数示例：{"prompt": "生成内容", "output_file": "plugin/nginx/main.yaml", "format": "yaml"}

4. **验证任务 (validation)** - 质量检查、格式验证等
   - 参数示例：{"files": ["plugin/xxx"], "check_type": "format"}

5. **文件操作 (file_op)** - 文件操作任务
   - 参数示例：{"operation": "write", "file_path": "xxx", "content": "..."}

6. **目录操作 (dir_op)** - 创建目录结构
   - **重要**：必须使用 directories 参数，提供要创建的目录列表
   - **路径要求**：所有目录必须以 plugin/ 开头
   - 参数格式：{"directories": ["plugin/xxx", "plugin/xxx/subdir1", "plugin/xxx/subdir2"]}
   - 示例：创建 nginx 插件目录结构
     {"directories": ["plugin/nginx", "plugin/nginx/workspace", "plugin/nginx/doc"]}

7. **自定义任务 (custom)** - 其他特殊需求
   - 参数根据具体需求自定义
"""
    
    @staticmethod
    def get_document_analysis_focus() -> str:
        """获取文档分析重点"""
        return """
分析重点：
1. 软件的基本信息（名称、版本、用途等）
2. 系统环境要求和依赖
3. 安装和配置步骤
4. 服务管理方法
5. 安全和权限要求
6. 故障排除信息"""
    
    @staticmethod
    def format_requirements_list(requirements: List[str]) -> str:
        """格式化要求列表"""
        return "\n".join(f"- {req}" for req in requirements)
    
    @staticmethod
    def format_quality_check_items(items: Dict[str, List[str]]) -> str:
        """格式化质量检查项目"""
        result = []
        for category, checks in items.items():
            result.append(f"{category}")
            for check in checks:
                result.append(f"   - {check}")
            result.append("")
        return "\n".join(result)
