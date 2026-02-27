"""
任务提示词构建器 - 构建任务规划和执行相关的提示词

任务提示词用于指导AI Agent进行任务规划、执行、调整和重试。
"""

from typing import Dict, Any
from doc2plugin.prompts.components import PromptComponents, PromptConfig


class TaskPromptBuilder:
    """任务提示词构建器"""
    
    def __init__(self):
        """初始化任务提示词构建器"""
        self.components = PromptComponents()
        self.config = PromptConfig()
    
    def build_task_planning_prompt(self, target: str, prompt: str, mode: str, 
                                   has_develop_doc: bool = False) -> str:
        """
        构建任务规划提示词
        
        Args:
            target: 用户目标
            prompt: 环境约束
            mode: 模式类型
            has_develop_doc: 是否有开发文档
        """
        base_prompt = f"""
请根据用户需求和项目现状，生成一个灵活的任务执行计划。

用户目标：{target}

环境要求：{prompt}

模式类型：{mode}"""
        
        # 添加开发文档相关提示
        if mode != 'shell' and has_develop_doc:
            base_prompt += """

**重要提示**：你已在系统提示词中收到完整的开发文档。
请根据该文档中的规范和要求设计任务流程，确保生成的项目完全符合文档标准。
任务的设计要体现文档中定义的目录结构、文件格式、技术要求等。"""
        
        base_prompt += """

**重要提示：在开发多文件项目时，必须遵循以下工作流程：**

1. **第一步：规划文件结构** - 创建一个 analysis 类型的任务，输出 cache/file_manifest.json
   - 该任务必须列出所有需要生成的文件及其详细实现方案
   - 文件清单格式示例（必须包含implementation字段）：
   ```json
   {
     "files": [
       {
         "path": "plugin/xxx/main.py",
         "description": "主程序文件",
         "depends_on": ["plugin/xxx/config.yaml"],
         "implementation": {
           "purpose": "作为项目入口，解析参数、加载配置、调用核心功能",
           "parameters": ["命令行参数: --mode", "环境变量: PROJECT_HOME"],
           "referenced_files": ["读取config.yaml配置", "调用utils.py工具函数"],
           "steps": ["1. 解析命令行参数", "2. 加载配置文件", "3. 执行主逻辑"],
           "notes": ["需要完整的错误处理", "所有路径使用绝对路径"]
         }
       },
       {
         "path": "plugin/xxx/config.yaml",
         "description": "配置文件",
         "depends_on": [],
         "implementation": {
           "purpose": "定义所有可配置参数",
           "parameters": ["install_path", "port", "log_level"],
           "referenced_files": [],
           "steps": ["1. 定义配置项", "2. 设置默认值", "3. 添加注释"],
           "notes": ["使用YAML格式", "所有配置项必须有注释"]
         }
       }
     ]
   }
   ```
   - **关键**：implementation字段是必需的，包含5个子字段(purpose, parameters, referenced_files, steps, notes)
   - 这些详细信息将直接指导后续LLM生成代码，避免发散和不一致

2. **第二步：创建目录结构** - 创建所有必需的目录

3. **第三步及之后：生成文件** - 为每个文件创建独立的 generation 任务
   - **关键要求**：每个 generation 任务的 parameters.input_files 必须包含 "cache/file_manifest.json"
   - 每个任务必须依赖 "plan_file_structure" 任务
   - 在生成文件时，LLM 会读取文件清单和详细的implementation方案，确保严格遵循

4. **最后：验证** - 验证所有文件是否按照清单生成
"""
        
        base_prompt += f"""
{self.components.get_available_tools()}

请分析项目现状和用户需求，设计一个适合的任务列表。{self.components.get_task_types_description()}

{self._get_task_json_format()}

**重要：所有生成的项目文件必须放在 plugin/ 目录下！**

**重要说明**：
系统会自动根据文件清单生成所有必要的任务（创建目录、生成文件、验证）。
LLM 只需关注生成高质量的文件清单，确保：
1. 所有需要生成的文件都列在清单中
2. 文件路径准确（必须以 plugin/ 开头）
3. 文件依赖关系正确（depends_on 字段）
4. 被其他文件引用的文件必须在清单中列出
5. **每个文件必须包含完整的implementation字段**，包含5个子字段：
   - purpose: 该文件的详细作用和职责
   - parameters: 使用的配置参数、环境变量、命令行参数等
   - referenced_files: 引用的项目内其他文件及引用方式
   - steps: 实现的主要功能步骤（按顺序）
   - notes: 开发时需要注意的点（错误处理、边界条件等）
6. implementation信息越详细越好，这将直接指导后续代码生成，避免不一致和遗漏"""
        
        return base_prompt
    
    def build_task_adjustment_prompt(self, current_tasks: str, issue_description: str) -> str:
        """
        构建任务调整提示词
        
        Args:
            current_tasks: 当前任务列表的JSON字符串
            issue_description: 遇到的问题描述
        """
        return f"""
当前任务执行过程中遇到了问题，需要调整任务计划。

当前任务列表：
{current_tasks}

遇到的问题：
{issue_description}

请分析问题原因，并调整任务计划：
1. 识别问题的根本原因
2. 确定需要修改或添加的任务
3. 调整任务的依赖关系
4. 更新任务参数和验证规则

请返回调整后的完整任务列表（JSON格式），确保能够解决当前问题。"""
    
    def build_task_retry_prompt(self, task_name: str, error_message: str, retry_count: int) -> str:
        """
        构建任务重试提示词
        
        Args:
            task_name: 任务名称
            error_message: 错误信息
            retry_count: 当前重试次数
        """
        return f"""
任务 "{task_name}" 执行失败，正在进行第 {retry_count} 次重试。

错误信息：
{error_message}

请分析失败原因并调整执行策略：
1. 分析错误的具体原因
2. 确定是否需要修改任务参数
3. 调整执行方法或提示词
4. 提供更详细的错误处理

请提供改进后的执行方案，确保任务能够成功完成。"""
    
    def build_quality_check_prompt(self) -> str:
        """构建质量检查提示词"""
        check_items = self.components.format_quality_check_items(self.config.QUALITY_CHECK_ITEMS)
        
        return f"""
请对生成的部署脚本和文档进行质量检查：

检查项目：
{check_items}

请提供详细的检查结果和改进建议。"""
    
    def _get_task_json_format(self) -> str:
        """获取任务JSON格式示例"""
        return """
**重要：请直接返回纯JSON格式的任务列表，不要使用Markdown代码块（```json），不要添加任何其他文字说明。**

JSON格式要求：
- 必须是有效的JSON数组，以 [ 开头，以 ] 结尾
- 每个任务必须包含以下字段：
  * id: 任务唯一标识（字符串）
  * name: 任务名称（字符串）
  * description: 任务描述（字符串）
  * type: 任务类型（字符串，必须是以下之一：analysis, extraction, generation, validation, file_op, dir_op, custom）
  * dependencies: 依赖的任务ID列表（数组）
  * parameters: 任务参数（对象）
  * expected_outputs: 期望的输出文件列表（数组）
  * max_retries: 最大重试次数（数字，默认3）

示例（请按此格式直接输出纯JSON）：
[
  {
    "id": "plan_file_structure",
    "name": "规划文件结构",
    "description": "根据开发文档规划所有需要生成的文件清单",
    "type": "analysis",
    "dependencies": [],
    "parameters": {
      "prompt": "根据提纯后的文档和用户需求，列出所有需要生成的文件及其作用，生成完整的文件清单",
      "input_files": ["cache/source.md"],
      "output_file": "cache/file_manifest.json"
    },
    "expected_outputs": ["cache/file_manifest.json"],
    "max_retries": 3
  },
  {
    "id": "create_structure",
    "name": "创建目录结构",
    "description": "创建插件的目录结构",
    "type": "dir_op",
    "dependencies": ["plan_file_structure"],
    "parameters": {
      "directories": ["plugin/nginx", "plugin/nginx/workspace", "plugin/nginx/doc"]
    },
    "expected_outputs": ["plugin/nginx/", "plugin/nginx/workspace/", "plugin/nginx/doc/"],
    "max_retries": 3
  },
  {
    "id": "generate_main_file",
    "name": "生成主配置文件",
    "description": "生成主配置文件（参考文件清单）",
    "type": "generation",
    "dependencies": ["create_structure", "plan_file_structure"],
    "parameters": {
      "prompt": "根据cache/file_manifest.json中的规划，生成主配置文件",
      "input_files": ["cache/source.md", "cache/file_manifest.json"],
      "output_file": "plugin/nginx/main.yaml"
    },
    "expected_outputs": ["plugin/nginx/main.yaml"],
    "max_retries": 3
  }
]

请直接输出JSON数组，不要添加任何说明文字或Markdown符号。"""
