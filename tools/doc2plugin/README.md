# doc2plugin

🤖 **AI Agent 智能代码编写工具**

自动将部署文档转换为可执行脚本。

## ✨ 特性

- 🧠 **智能理解**：基于 LLM 的文档智能分析
- 🔧 **自动生成**：文档到脚本的一键转换
- 📖 **文档驱动**：支持 Shell、oeDeploy 等多种输出格式
- 🔄 **灵活适配**：支持有/无文档两种使用场景
- 📋 **精确约束**：通过文件清单和详细实现方案确保多文件项目的一致性
- 🎯 **结构化提示词**：统一的消息构建，开发文档始终在SystemMessage中确保高优先级
- 🔒 **严格JSON格式**：所有LLM输出统一使用JSON格式，提高解析可靠性
- 🔀 **操作独立**：compose、test、modify三种操作完全独立，各自加载对应的文档和提示词

## 🚀 快速开始

### 安装

```bash
git clone <repository-url>
cd doc2plugin
pip install -r requirements.txt
pip install -e .
doc2plugin --version
```

### 使用流程

**1. 初始化项目**

```bash
doc2plugin init
```

**2. 准备文档（可选）**

将部署文档放入 `doc/` 目录。如无文档，系统将根据任务描述生成脚本。

```bash
cp your-docs/* doc/
```

**3. 配置任务**

编辑 `work.yaml` 配置 LLM 和任务信息：

```yaml
llm_info:
  base_url: 'https://api.deepseek.com/v1'
  api_key: 'your-api-key'
  model_name: 'deepseek-chat'
  temperature: 0.1

task:
  target: '根据文档编写 Nginx 部署脚本'
  prompt: '部署环境为 openEuler，拥有 sudo 权限'
  mode: 'shell'  # shell 或 oedp
```

**4. 生成脚本**

```bash
doc2plugin compose
```

生成的脚本位于 `plugin/` 目录。

**5. 测试脚本（可选）**

```bash
doc2plugin test
```

自动生成测试脚本 `cache/test.sh` 并执行，测试日志输出到 `cache/test.log`。如果两个文件已同时存在，则跳过生成步骤，从而支持测试与修改交替进行。

**6. 修改代码（可选）**

```bash
doc2plugin modify
```

如果测试失败，可以运行此命令基于测试结果自动修改代码或测试脚本。

## 🔧 命令

| 命令 | 说明 |
|------|------|
| `doc2plugin init` | 初始化项目目录和配置文件 |
| `doc2plugin compose` | 分析文档并生成脚本 |
| `doc2plugin test` | 测试已生成的代码（test.sh和test.log如果同时存在，则跳过生成测试脚本，从而支持测试/优化交替进行。） |
| `doc2plugin modify` | 基于测试结果修改代码 |
| `doc2plugin status` | 检查项目状态 |
| `doc2plugin clean [-f]` | 清理生成的文件（-f 跳过确认） |

## ⚙️ 配置说明

### LLM 配置（llm_info）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `base_url` | API 服务地址 | - |
| `api_key` | API 密钥 | - |
| `model_name` | 模型名称 | - |
| `timeout` | 超时时间（秒） | 600 |
| `temperature` | 生成温度（0.0-2.0） | 0.1 |
| `max_tokens` | 最大令牌数 | null |

支持 OpenAI API、Azure OpenAI、硅基流动、智谱 AI 等兼容服务。

### 任务配置（task）

| 参数 | 说明 | 示例 |
|------|------|------|
| `target` | 任务目标 | `根据文档编写 Nginx 部署脚本` |
| `prompt` | 环境约束和要求 | `openEuler 系统，sudo 权限` |
| `mode` | 输出模式 | `shell` 或 `oedp` |

## 📖 使用示例

### 示例 1：基于文档生成 Shell 脚本

将 Nginx 部署文档放入 `doc/` 目录，配置：

```yaml
task:
  target: '根据文档编写 Nginx 部署脚本，支持 install 和 uninstall'
  prompt: 'openEuler 系统，sudo 权限'
  mode: 'shell'
```

生成：`plugin/deploy.sh`、`plugin/readme.md`

### 示例 2：无文档生成脚本

`doc/` 目录为空时，在任务描述中提供详细需求：

```yaml
task:
  target: '编写 Nginx 安装脚本，支持安装、启动和卸载'
  prompt: 'openEuler 系统，yum 包管理，sudo 权限，端口 80'
  mode: 'shell'
```

### 示例 3：生成 oeDeploy 插件

```yaml
task:
  target: '创建 Nginx 的 oeDeploy 插件'
  prompt: 'openEuler 系统，单节点部署'
  mode: 'oedp'
```

生成完整的插件目录结构（main.yaml、config.yaml、playbook 等）。

### 示例 4：测试生成的代码

```bash
# 先生成代码
doc2plugin compose

# 然后测试
doc2plugin test
```

系统会自动生成测试脚本并执行，验证生成的代码是否符合预期功能。test.sh和test.log如果同时存在，则跳过生成测试脚本，从而支持测试与修改交替进行。

### 示例 5：修改代码

```bash
# 如果测试失败，运行修改命令
doc2plugin modify

# 修改后重新测试
doc2plugin test
```

系统会分析测试日志，自动修改有问题的代码或测试脚本，然后可以重新测试验证。

## 🏗️ 扩展新模式

添加新模式只需 3 步，无需修改代码：

1. **编写文档**：创建 `doc/YourMode.md` 和 `doc/YourModeTest.md`
2. **配置模式**：编辑 `config/modes.yaml`
3. **使用模式**：在 `work.yaml` 中设置 `mode: 'your_mode'`

## 🐛 故障排除

### 问题诊断

**检查项目状态**

```bash
doc2plugin status  # 检查项目状态和配置
```

**查看日志**

```bash
cat cache/agent.log  # 系统执行日志、终端输出记录和token统计
cat cache/llm.log    # LLM完整交互记录（输入输出无截断、详细token统计）
```

日志中会自动记录每次LLM调用的token消耗情况，便于统计和优化成本。

### 常见问题

| 问题 | 解决方法 |
|------|----------|
| 配置错误 | 检查 `work.yaml` 中的 API 密钥、地址是否正确 |
| 生成不完整 | 在 `target` 和 `prompt` 中提供更详细的需求描述 |
| 无文档警告 | 系统支持无文档运行，在任务配置中详细描述需求即可 |
| LLM 调用失败 | 检查网络连接、API 配额、模型名称是否正确 |
| 项目结构错误 | 运行 `doc2plugin status` 检查，缺失目录会自动创建 |

