# doc2plugin 设计文档

## 项目概述

doc2plugin 是一个基于 LangChain 开发的 AI Agent 工具，能够将软件部署文档智能转换为可执行的部署脚本。

**核心特性**：
- **文档驱动架构**：通过开发文档定义项目规范，LLM 根据文档自动生成符合要求的项目，无需修改代码即可扩展新模式
- **灵活的输入方式**：支持基于文档生成和基于任务描述生成两种模式，适应不同使用场景

## 系统架构

### 整体架构

```
用户配置 (work.yaml) → 配置管理器 (config_manager.py)
                         ├─ 读取 modes.yaml
                         ├─ 加载开发文档
                         └─ 解析配置参数
                               ↓
                      AI Agent (core.py)
                         ├─ 初始化 LLM
                         ├─ 注入开发文档到提示词
                         └─ 启动工作流管理器
                               ↓
                  工作流管理器 (langgraph_workflow.py)
                         ├─ 文档提纯（可选）
                         ├─ 生成任务计划（含文件清单）
                         ├─ 执行任务循环
                         ├─ 验证任务结果
                         └─ 基于LangGraph的状态管理
                               ↓
                     通用工具集 (tools/)
                         ├─ 文件读写
                         ├─ 目录操作
                         └─ 文件列表
```

### 核心模块

**命令模块** (`doc2plugin/commands/`):
- `base_command.py`: 命令基类，定义命令接口
- `init_command.py`: 初始化项目结构和配置
- `compose_command.py`: AI代码生成命令（compose操作）
- `test_command.py`: 测试脚本生成和执行命令（test操作）
- `modify_command.py`: 基于测试结果修改代码命令（modify操作）
- `status_command.py`: 项目状态检查命令
- `clean_command.py`: 清理生成文件命令

**CLI入口** (`doc2plugin/cli.py`):
- 命令行接口入口，使用Click库实现

**Agent模块** (`doc2plugin/agent/`):
- `core.py`: AI Agent核心协调器，整合配置、LLM、工具和工作流
- `langgraph_workflow.py`: 基于LangGraph的工作流管理系统，负责任务编排和执行

**提示词模块** (`doc2plugin/prompts/`):
- `prompt_manager.py`: 统一的提示词管理器
- `system_prompts.py`: 系统级提示词构建器
- `task_prompts.py`: 任务规划和执行提示词
- `document_prompts.py`: 文档处理提示词
- `agent_prompts.py`: Agent执行时的提示词模板（主入口）
- `file_generation_prompts.py`: 文件生成相关提示词构建器
- `context_builder.py`: 上下文构建器（文件清单、目录树等）
- `constants.py`: 提示词常量（格式要求、示例、占位符等）
- `components.py`: 可复用的提示词组件

**工具模块** (`doc2plugin/tools/`):
- `file_tools.py`: 文件操作工具（读、写、删、列表）
- `directory_tools.py`: 目录操作工具（创建、删除）
- `tool_registry.py`: 工具注册表

**通用模块** (`doc2plugin/utils/`):
- `llm_client.py`: LLM客户端（LLM调用、重试、内容提取、token统计）
- `terminal_output.py`: 终端输出管理（美化输出，自动同步到agent.log）
- `agent_logger.py`: 统一的agent日志管理（全局共享的agent.log记录器）
- `project_manager.py`: 项目管理器（项目结构验证、配置验证、文件检查等公共功能）

**配置管理** (`doc2plugin/config_manager.py`):
- 配置和文档管理（文档驱动核心）
- 模式配置位于 `config/modes.yaml`

## 文档驱动架构

### 核心设计理念

1. **开发文档是唯一信息源**：所有模式特定的知识来自开发文档，不在代码中硬编码
2. **代码与模式完全解耦**：核心代码不包含任何模式特定的逻辑
3. **配置驱动扩展**：通过 `modes.yaml` 添加新模式，无需修改代码
4. **LLM 自主理解**：LLM 根据开发文档自主决定项目结构和实现

### 工作流程

```
work.yaml (mode: "oedp")
    ↓
ConfigManager 读取 modes.yaml
    ↓
加载对应的开发文档和专用提示词
    ↓
PromptManager 注入文档到系统提示词
    ↓
LLM 理解规范并生成任务计划
    ↓
WorkflowManager 执行任务
    ↓
使用通用工具 (file_write, directory_create)
    ↓
生成符合规范的项目
```

### 添加新模式

只需三步，无需修改代码：

**1. 编写开发文档**

创建 `doc/NewMode.md` 和 `doc/NewModeTest.md`，定义项目结构、文件格式和测试要求。

**2. 配置模式** (`config/modes.yaml`)

```yaml
new_mode:
  compose:
    doc_path: ["doc/NewMode.md"]
    prompt: ["遵循开发文档规范"]
    description: "代码生成"
  test:
    doc_path: "doc/NewModeTest.md"
    prompt: ["覆盖主要功能"]
    description: "代码测试"
  modify:
    doc_path: ["doc/NewMode.md", "doc/NewModeTest.md"]
    prompt: ["分析测试结果，修改代码以通过测试"]
    description: "代码修改"
```

**3. 使用模式** (`work.yaml`)

```yaml
task:
  mode: "new_mode"
  target: "你的目标"
```

## 核心机制

### 1. 文档提纯机制

**目的**：将 doc/ 目录下的文档提炼为 cache/source.md，过滤干扰信息，作为后续任务的统一上下文。

**工作流程**：
```
doc/*.* (可选) → LLM提炼关键信息 → cache/source.md
                        ↓
                 后续所有任务使用统一上下文
```

**执行策略**：
- 作为独立步骤（步骤0），在生成任务计划之前执行
- 最多执行一次（使用内存变量标记）
- 至少执行一次（覆盖已存在的 cache/source.md）

**容错机制**：
- doc/ 目录为空时，生成包含占位符的 cache/source.md
- 所有后续任务检测 cache/source.md 不存在时使用占位符
- 异常捕获，记录错误但不中断流程

### 2. 文件清单管理机制

**目的**：解决多文件项目生成时的一致性问题（文件引用错误、路径不一致、代码不兼容等）。

**三阶段实现**：

**阶段1：规划**
- LLM 分析需求和开发文档
- 生成完整的文件清单 JSON（cache/file_manifest.json）
- 每个文件包含详细的实现方案（implementation字段）：
  * `purpose`: 文件的详细作用和职责
  * `parameters`: 需要使用的配置参数、环境变量等
  * `referenced_files`: 引用的其他文件的详细说明
  * `steps`: 需要实现的主要功能步骤
  * `notes`: 开发时需要特别注意的点

**阶段2：执行**
- 每个文件生成任务自动读取文件清单
- 生成目录树结构，展示项目结构
- 在提示词中展示文件清单和完整的实现方案（包含purpose、parameters、referenced_files、steps、notes五个字段）
- 使用明显的分隔符（80个=）标识"参考内容"和"核心约束"区域
- 在已生成文件之间使用分隔符（60个=）增强可读性
- 要求LLM严格遵循规划阶段确定的实现方案

**阶段3：验证**
- 对比生成的文件与清单
- 检查是否有遗漏或多余的文件
- 详细日志记录

**文件清单示例**：
```json
{
  "files": [
    {
      "path": "plugin/myapp/main.py",
      "description": "主程序文件",
      "depends_on": ["plugin/myapp/utils.py"],
      "implementation": {
        "purpose": "作为项目入口，解析参数、调用核心功能",
        "parameters": ["命令行参数: --mode (install/uninstall)"],
        "referenced_files": ["调用utils.py中的日志函数和工具函数"],
        "steps": [
          "1. 解析命令行参数",
          "2. 调用对应的功能函数",
          "3. 处理异常"
        ],
        "notes": ["需要完整的错误处理", "退出码: 0成功, 1失败"]
      }
    },
    {
      "path": "plugin/myapp/utils.py",
      "description": "工具函数模块",
      "depends_on": [],
      "implementation": {
        "purpose": "提供日志记录和通用工具函数",
        "parameters": ["日志文件路径: /var/log/myapp.log"],
        "referenced_files": [],
        "steps": [
          "1. 实现日志函数",
          "2. 实现文件操作函数",
          "3. 实现命令执行函数"
        ],
        "notes": ["所有函数要有异常处理", "日志支持多级别"]
      }
    }
  ]
}
```

**核心优势**：
- 一致性保证：所有文件引用都基于统一的清单
- 可见性增强：文件清单以目录树形式在提示词中明确展示，包含完整的implementation详情
- 优先级最高：文件清单约束在LLM上下文中具有最高优先级，使用明显分隔符标识
- 实现方案详细：每个文件的implementation字段包含5个子字段，直接指导LLM生成代码
- 完整性检查：验证阶段确保不遗漏任何文件
- 格式清晰：使用分隔符提高提示词的结构化和可读性

### 3. 已生成文件上下文传递机制

**目的**：确保生成后续文件时，LLM能够看到已生成的文件内容，避免不兼容问题。

**实现方案**：
- **自动读取**：在生成每个文件时，自动读取 plugin/ 目录下所有已生成的文件
- **上下文注入**：将所有已生成文件的内容注入到 LLM 的上下文中
- **结构化展示**：使用分隔符（60个=）在文件内容之间增强可读性
- **兼容性提醒**：在提示词中明确要求 LLM 检查新文件与已生成文件的兼容性

**关键检查点**：
- 文件路径引用必须一致
- 配置项名称和格式必须匹配
- 变量名、函数名、类名等必须保持一致
- 模块导入路径必须正确

## 核心模块实现

### 1. 配置管理模块 (`config_manager.py`)

**职责**：文档驱动的配置管理，是整个系统的核心枢纽

**主要功能**：
- 读取 `modes.yaml` 模式配置
- 根据模式自动加载开发文档（支持单个或多个文档）
- 根据模式加载专用提示词（`prompt` 字段）
- 解析 `work.yaml` 中的 LLM 和任务配置
- 将开发文档内容和模式专用提示词注入到 LLM 上下文

**关键类**：
- `ModeType`: 模式类型枚举（SHELL, OEDP 等）
- `LLMConfig`: LLM 服务配置
- `TaskConfig`: 任务配置（target, prompt, mode）
- `LLMContextConfig`: LLM 上下文（包含开发文档和模式专用提示词）

**设计特点**：
- 支持action级别配置（compose、test等）
- 支持单个或多个开发文档
- 支持模式专用提示词

### 2. AI Agent 核心模块 (`agent/core.py`)

**职责**：核心协调器，整合配置、LLM、工具和工作流

**初始化流程**：
1. 创建Agent时指定操作类型（action: 'compose', 'test', 'modify'）
2. 加载配置（自动加载对应操作的文档和提示词）
3. 初始化LLM和客户端
4. 初始化提示词管理器
5. 初始化工具和工作流管理器

**操作分离机制**：
- compose、test、modify三种操作完全独立
- 每种操作在初始化Agent时指定，直接加载对应的文档和提示词
- 避免运行时切换配置，简化逻辑，减少混淆

### 3. 工作流管理模块 (`agent/langgraph_workflow.py`)

**职责**：基于LangGraph的工作流管理，负责任务编排和执行

**工作流**：
- **compose流程**：文档提纯 → 生成文件清单 → 生成任务 → 执行任务 → 检查完成
- **test流程**：检查缓存 → 构建上下文 → LLM生成测试脚本（JSON格式） → 执行测试脚本（test.sh和test.log如果同时存在，则跳过生成测试脚本，从而支持测试与修改交替进行）
- **modify流程**：构建上下文 → LLM分析生成修改清单（JSON格式） → 执行修改任务

**统一的消息构建**：
- 所有操作（compose、test、modify）统一使用`prompts.format_messages(mode, human_prompt)`构建LLM消息
- 开发文档和模式专用提示词始终在SystemMessage中，确保高优先级
- 任务上下文和具体要求在HumanMessage中

**通用上下文构建**：
- test和modify操作共享`_build_common_context()`方法
- 避免重复代码，提高可维护性

### 4. 提示词模块 (`prompts/`)

**职责**：文档驱动的提示词生成和管理

**设计特点**：
- 职责清晰：每个模块专注特定类型的提示词
- 避免重复：公共内容提取到 constants.py
- 易于维护：新增提示词只需修改对应模块
- 上下文构建：专门的 ContextBuilder 负责复杂的上下文组装
- 统一消息格式：`PromptManager.format_messages()`统一构建SystemMessage和HumanMessage
- 文档优先：开发文档和模式专用提示词始终在SystemMessage中，确保最高优先级

### 5. LLM 客户端模块 (`utils/llm_client.py`)

**职责**：统一的LLM调用接口

**核心功能**：
- 自动重试机制
- 流式输出
- LLM专用日志：llm.log（完整记录LLM输入输出，无截断）
- Token统计：使用tiktoken库精确估算输入输出的token数量

### 6. 终端输出模块 (`utils/terminal_output.py`)

**职责**：美化的终端输出

**核心功能**：
- 基于 Rich 库实现
- 支持流式内容实时更新
- 统一的图标和颜色
- 自动同步输出到agent.log

### 7. Agent日志模块 (`utils/agent_logger.py`)

**职责**：统一的agent日志管理

**核心功能**：
- 全局共享的日志记录器
- 所有模块通过该模块记录agent.log
- 单例模式确保日志一致性

### 8. 工具集模块 (`tools/`)

**职责**：提供通用文件系统操作工具，不包含任何模式特定逻辑

**工具列表**：
- `FileListTool`: 列出目录文件
- `FileReadTool`: 读取文件
- `FileWriteTool`: 写入文件
- `FileDeleteTool`: 删除文件
- `DirectoryCreateTool`: 创建目录
- `DirectoryDeleteTool`: 删除目录

**设计原则**：
- 提供通用文件系统操作
- 所有操作限制在项目目录内

### 9. 命令实现模块 (`commands/`)

**职责**：实现各种命令的具体逻辑

**主要命令**：
- `init`: 创建项目结构和配置模板
- `compose`: 启动 Agent 执行代码编写（创建Agent时指定action='compose'）
- `test`: 生成测试脚本并执行（创建Agent时指定action='test'，如test.sh和test.log已存在则跳过生成）
- `modify`: 基于测试结果修改代码（创建Agent时指定action='modify'）
- `status`: 检查项目完整性
- `clean`: 清理生成文件

**设计原则**：
- 命令类继承 `BaseCommand`，实现 `execute` 方法
- 创建Agent时传入对应的action参数，确保加载正确的文档和提示词
- 使用 `terminal` 模块输出到终端（自动同步到agent.log）
- 使用 `setup_agent_logger` 和 `get_agent_logger` 记录agent.log
- 使用 `ProjectManager` 处理项目结构验证等公共操作

### 10. CLI 接口模块 (`cli.py`)

**职责**：命令行入口

**支持命令**：init、compose、test、status、clean

### 11. 项目管理模块 (`utils/project_manager.py`)

**职责**：提供项目相关的公共静态方法

**主要功能**：
- `validate_project_structure`: 验证项目结构，自动创建缺失目录
- `check_documents`: 检查文档文件
- `check_plugin_files`: 检查已生成的插件文件
- `check_test_artifacts`: 检查测试产物（测试脚本和日志）
- `validate_config`: 验证配置文件

**设计特点**：
- 所有方法为静态方法，无需实例化
- 集中管理项目相关的验证和检查逻辑
- 使用 `terminal` 输出用户友好的提示（自动同步到agent.log）

## 数据流设计

### 项目目录结构

```
project/
├── doc/                # 输入：原始文档（可选）
├── plugin/             # 输出：生成的脚本（结构由 LLM 决定）
├── cache/              # 日志和中间文件
│   ├── agent.log       # Agent 执行日志
│   ├── llm.log         # LLM 交互日志
│   ├── file_manifest.json  # 文件清单
│   ├── modification_manifest.json  # 修改清单
│   ├── tasks.json      # 任务计划
│   ├── source.md       # 提炼文档
│   ├── test.sh         # 测试脚本
│   └── test.log        # 测试日志
└── work.yaml           # 配置文件
```

### 数据转换流程

```
doc/*.* (可选) → 文档提纯 → cache/source.md
                            ↓
                cache/source.md → LLM 分析 → cache/file_manifest.json
                            ↓
                cache/source.md + 文件清单 → 生成 plugin/*
                            ↓
                        验证所有文件齐全
```

**说明**：
- 文档提纯阶段：将 doc/ 目录下所有文档提炼成 `cache/source.md`
- 如果 doc/ 目录为空，使用占位符
- 所有后续任务使用 `cache/source.md` 作为统一上下文
- LLM 根据提纯后的文档和 work.yaml 中的 `target` 和 `prompt` 生成输出

## 配置管理

### work.yaml 配置

```yaml
llm_info:
  base_url: "https://api.deepseek.com/v1"
  api_key: "your-api-key"
  model_name: "deepseek-chat"
  timeout: 600
  temperature: 0.1
  max_tokens: null  # null 表示不限制
  max_llm_retries: 3  # LLM调用最大重试次数
  llm_retry_delay: 1.0  # 重试延迟（秒），使用指数退避策略

task:
  target: "任务目标"
  prompt: "环境约束"
  mode: "shell"  # shell 或 oedp
```

### modes.yaml 配置

配置文件位置：`config/modes.yaml`

```yaml
oedp:
  compose:
    doc_path: ["doc/oedp/DevelopInstruction.md", "doc/oedp/Command.md"]
    prompt: ["遵循开发文档规范"]
    description: "生成 oeDeploy 插件"
  test:
    doc_path: "doc/oedp/TestInstruction.md"
    prompt: ["覆盖主要功能"]
    description: "测试 oeDeploy 插件"
```

**配置结构**：
- 每个模式下配置多个操作（`compose`、`test`等）
- 每个操作包含：`doc_path`（文档路径）、`prompt`（专用提示词）、`description`（描述）

## 日志系统

### 双日志设计

**1. agent.log**：系统执行日志
- 执行流程、任务进度、文件操作
- 记录命令模块和Agent模块的日志
- 记录所有终端输出（移除 ANSI 颜色代码）
- LLM调用统计：记录每次LLM调用的输入输出长度（字符数和token数）

**2. llm.log**：LLM 交互日志
- 完整记录输入消息（System/Human）
- 完整记录 LLM 响应（不截断）
- 包含交互阶段标识
- 长度统计：记录每次交互的输入输出长度（字符数和token数）

### LLM调用长度记录

**自动记录机制**（通过 Callbacks）：
- 系统使用 `LoggingCallbackHandler` 自动记录每次LLM调用
- **输入长度**：通过 `on_chat_model_start` 自动统计字符数和token数
- **输出长度**：通过 `on_llm_end` 自动统计字符数和token数
- **Token估算**：使用 `tiktoken` 库精确估算token数量
  * 优先使用tiktoken库（OpenAI官方推荐）
  * 如tiktoken不可用，使用简单估算：中文约1.5字符=1token，英文约4字符=1token
  * 根据模型名称自动选择合适的tokenizer编码器

## 错误处理

### 分层处理

- **CLI 层**：输入验证，友好提示
- **命令层**：业务逻辑验证
- **Agent 层**：LLM 调用异常
- **工具层**：文件操作异常

### 恢复机制

- 自动重试（LLM 调用、任务执行）
- 详细日志记录
- 智能任务调整

### JSON格式解析

- 文件清单生成：使用JSON格式，包含完整的implementation字段
- 测试脚本生成：使用JSON格式 `{"script_content": "..."}`
- 修改清单生成：使用JSON格式 `{"analysis": "...", "operations": [...]}`
- 文件内容生成：使用JSON格式 `{"file_content": "..."}`
- 统一使用`JsonOutputParser`和`json.loads()`解析，避免手动提取

## 扩展性设计

### 添加新模式

无需修改代码，只需：
1. 编写开发文档（定义规范）
2. 在 `modes.yaml` 中配置
3. 在 `work.yaml` 中使用

### 添加新工具

1. 继承 `BaseTool`
2. 实现 `_run` 方法
3. 在 `get_all_tools` 中注册

### 添加新命令

1. 继承 `BaseCommand`，实现 `execute` 方法
2. 在 CLI 中注册命令

## 关键设计原则

1. **文档驱动**：模式规范来自开发文档，不在代码中硬编码
2. **完全解耦**：核心代码不包含模式特定逻辑
3. **通用工具**：只提供文件系统操作，LLM 自主决定使用方式
4. **任务驱动**：根据项目状态和文档要求生成任务计划
5. **智能调整**：任务失败时自动分析和调整策略
6. **文档提纯**：提炼文档过滤干扰信息，提高生成质量
7. **文件清单管理**：通过清单机制确保多文件项目的一致性
8. **上下文传递**：生成后续文件时自动读取已生成文件
9. **统一上下文**：所有任务使用提纯后的 `cache/source.md` 作为上下文
10. **模式专用提示词**：支持为每个模式和操作添加高优先级的专用提示词
11. **操作级别配置**：支持为每个模式配置多个操作（compose、test、modify），每个操作可以有独立的文档和提示词
12. **操作独立初始化**：不同操作在Agent初始化时指定，避免运行时切换配置
13. **职责清晰的日志系统**：llm.log记录LLM交互、终端输出提供用户反馈、agent.log记录系统执行
14. **代码复用**：公共功能集中在 `ProjectManager`，避免重复代码
