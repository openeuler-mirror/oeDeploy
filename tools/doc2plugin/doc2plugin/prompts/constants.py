"""
提示词常量 - 定义通用的提示词常量、格式说明和示例

本模块集中管理所有提示词中使用的常量、格式要求和示例，避免重复。
"""


class OutputFormat:
    """输出格式要求"""
    
    JSON_PURE = """
【重要】JSON输出格式要求：
1. 直接输出纯JSON内容，从 { 或 [ 开始
2. 不要使用任何markdown代码块标记（禁止使用 ```json 或 ``` ）
3. 不要添加任何解释文字或注释
4. 确保JSON格式完全有效，可以直接被json.loads()解析
5. 输出示例：{"key": "value"} 而不是 ```json\n{"key": "value"}\n```

请严格遵守以上格式要求！"""
    
    YAML_JINJA2_WARNING = """
**YAML/Ansible 语法要求**（非常重要）：
1. 当 Jinja2 模板变量（{{ variable }}）作为 YAML 值的开头时，**必须用引号包裹整个值**
2. 错误示例：
   name: {{ package_name }}          # ❌ 错误！
   command: {{ script_path }}         # ❌ 错误！
3. 正确示例：
   name: "{{ package_name }}"         # ✅ 正确！
   command: "{{ script_path }}"       # ✅ 正确！
4. 如果变量不在开头，可以不加引号：
   path: /usr/bin/{{ binary_name }}   # ✅ 正确
5. **务必检查所有 {{ }} 变量，确保符合以上规则**
"""


class FileManifestFormat:
    """文件清单格式定义"""
    
    IMPLEMENTATION_FIELDS = """
implementation字段说明（必需）：
1. **purpose**：该文件在整个项目中的详细作用和职责
2. **parameters**：该文件需要使用的配置参数、环境变量、命令行参数等（数组格式）
3. **referenced_files**：该文件会引用的项目内其他文件的详细说明（数组格式，每项说明引用方式）
4. **steps**：该文件需要实现的主要功能步骤（数组格式，按顺序列出）
5. **notes**：开发该文件时需要特别注意的点（数组格式，如错误处理、边界条件、兼容性等）

这些详细信息将直接指导后续的LLM生成该文件，确保生成的文件清单准确、一致、无遗漏。"""
    
    FILE_MANIFEST_REQUIREMENTS = """
文件清单格式要求：
1. 必须是有效的JSON对象，包含一个 "files" 数组
2. 每个文件对象必须包含以下字段：
   - path: 文件路径（必须以 plugin/ 开头）
   - description: 文件作用的简短说明（1-2句话）
   - depends_on: 该文件依赖的其他文件路径列表（如果在某个文件中引用了其他文件，必须在此列出）
   - implementation: 详细的实现方案说明对象，包含以下子字段：
     * purpose: 该文件在整个项目中的详细作用和职责
     * parameters: 该文件需要使用的配置参数、环境变量、命令行参数等（数组格式）
     * referenced_files: 该文件会引用的项目内其他文件的详细说明（数组格式，每项说明引用方式）
     * steps: 该文件需要实现的主要功能步骤（数组格式，按顺序列出）
     * notes: 开发该文件时需要特别注意的点（数组格式，如错误处理、边界条件、兼容性等）"""
    
    JSON_SCHEMA = """
示例（请输出纯JSON，不要使用代码块）：
{
  "files": [
    {
      "path": "plugin/myproject/main.py",
      "description": "主程序入口文件",
      "depends_on": ["plugin/myproject/config.yaml", "plugin/myproject/utils.py"],
      "implementation": {
        "purpose": "作为整个项目的入口点，负责解析命令行参数、加载配置、调用核心功能模块",
        "parameters": ["命令行参数: --config指定配置文件路径", "命令行参数: --mode指定运行模式(install/uninstall)"],
        "referenced_files": ["import config.yaml中的配置项", "调用utils.py中的辅助函数"],
        "steps": ["1. 解析命令行参数", "2. 加载config.yaml配置文件", "3. 根据mode参数调用对应的安装或卸载函数"],
        "notes": ["必须处理配置文件不存在的情况", "需要验证mode参数的有效性", "所有错误都要有清晰的错误提示"]
      }
    }
  ]
}"""
    
    REQUIREMENTS = """
**关键要求**：
1. 每个文件的implementation字段必须详细完整，这些信息将直接指导后续LLM生成代码
2. 如果某个文件引用了其他文件，必须在depends_on和implementation.referenced_files中都体现
3. implementation.steps要按照实际执行顺序列出，越详细越好
4. implementation.notes要包含所有关键的注意事项，帮助避免常见错误
5. 路径必须准确，不要遗漏任何文件
6. 只输出纯JSON，不要添加任何解释文字或Markdown标记
7. 根据开发文档中定义的项目结构和文件格式要求来规划文件列表"""


class ContextPrompts:
    """上下文相关的提示词"""
    
    MANIFEST_CONSTRAINT = """
【核心约束】文件清单与实现方案（高优先级）
你正在生成的文件是一个多文件项目的一部分。为了确保所有文件之间的一致性和完整性，
请严格遵循以下文件清单和实现方案：
1. **路径一致性**：如果你的代码需要引用其他文件（如 import、配置引用、脚本调用等），
   必须使用上述清单中的准确路径，禁止引用清单中不存在的文件。
2. **严格遵循实现方案**：
   - 必须按照implementation.steps中规定的步骤实现功能
   - 必须使用implementation.parameters中列出的参数
   - 必须实现implementation.notes中提到的所有注意事项
   - 引用其他文件时必须按照implementation.referenced_files中的说明
3. **完整性**：确保实现了所有必需的功能点，不要遗漏任何步骤
4. **一致性**：生成的代码必须与清单中的描述和实现方案保持一致，不要随意发散
"""
    
    DIRECTORY_TREE_HEADER = """
**项目目录结构**：
以下是完整的项目目录结构，所有文件路径引用必须严格遵循此结构：
"""
    
    MANIFEST_DETAILS_HEADER = """
**文件清单详情**：
"""
    
    GENERATED_FILES_HEADER = """
**【已生成文件】当前项目状态（共 {count} 个文件）**

以下是已经生成的文件内容，你在生成新文件时必须确保与这些文件兼容：

"""
    
    COMPATIBILITY_CHECK = """
**【兼容性检查】重要提醒**：

在生成新文件时，请特别注意以下兼容性问题：

1. **文件路径引用**：
   - 如果需要引用上述已生成的文件，路径必须完全一致
   - 例如：import语句、配置文件路径、脚本调用路径等
   
2. **配置项一致性**：
   - 如果引用了配置文件，配置项的名称和格式必须与已生成的配置文件完全匹配
   - 不要添加配置文件中不存在的配置项
   
3. **命名一致性**：
   - 变量名、函数名、类名等必须与已生成文件中的命名保持一致
   - 特别注意大小写和命名风格
   
4. **模块导入一致性**：
   - 如果需要导入其他模块，导入路径必须正确
   - 例如：from xxx import yyy，xxx必须是已生成的模块路径
   
5. **配置结构匹配**：
   - 如果读取或写入配置，配置的结构必须与已生成的配置文件匹配
   - 特别注意YAML/JSON的层级结构
   
6. **脚本调用路径**：
   - 如果需要调用其他脚本，路径必须是已生成的脚本的实际路径
   - 注意相对路径和绝对路径的使用

**请仔细检查上述已生成文件的内容，确保你生成的新文件能够与它们正确协同工作。**
"""


class PlaceholderContent:
    """占位符内容"""
    
    NO_DOC_PLACEHOLDER = """
# 提纯后的文档

## 说明
doc/ 目录为空或没有有效文档，无法提炼文档内容。
系统将根据 work.yaml 中的任务目标和约束条件继续执行。

请参考任务目标和环境约束来完成任务。
"""
    
    NO_DOC_WARNING = "doc/ 目录为空，无法进行文档提纯，将使用占位符内容"
