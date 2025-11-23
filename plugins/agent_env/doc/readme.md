# Agent 开发环境安装插件

## 插件简介

本插件用于快速安装 Agent 开发所需的 Python 环境和各类 Agent SDK。支持多种主流的 Agent 开发框架，只需简单配置即可一键部署。

## 支持的 Agent SDK

| SDK 名称 | 说明 |
|---------|------|
| **langchain** | LangChain框架，用于开发基于LLM的应用程序（默认） |
| **pyautogen** | Microsoft AutoGen框架，用于构建多智能体系统 |
| **agno** | Agno AI智能体框架 |
| **crewai** | CrewAI框架，用于编排角色扮演的自主AI智能体 |
| **google-generativeai** | Google的生成式AI Python SDK |
| **haystack-ai** | Haystack框架，用于构建基于LLM的NLP应用 |
| **openai** | OpenAI官方Python客户端库 |
| **smolagents** | HuggingFace的简单轻量级智能体框架 |

## 使用方法

### 1. 配置文件说明

编辑 `config.yaml` 文件，配置目标主机信息和 Agent SDK 类型：

```yaml
all:
  hosts:
    target-host:
      ansible_host: 127.0.0.1      # 目标主机IP地址
      ansible_port: 22              # SSH端口
      ansible_user: root            # 用户名
      ansible_password: ""          # 密码
  vars:
    # 选择要安装的Agent SDK类型
    agent_sdk: langchain           # 可选: pyautogen, agno, crewai, google-generativeai, 
                                   #       haystack-ai, langchain, openai, smolagents
    
    # pip源配置（默认使用华为云镜像）
    pip_index_url: https://mirrors.huaweicloud.com/repository/pypi/simple
    pip_trusted_host: mirrors.huaweicloud.com
```

### 2. 安装 Agent 开发环境

执行以下命令安装指定的 Agent SDK：

```bash
oedp run install
```

安装过程会自动完成以下步骤：
1. 检查并安装 python3 和 pip（如果不存在）
2. 使用 pip 安装指定 Agent SDK 的相关包
3. 运行验证脚本，确认安装成功

### 3. 卸载 Agent SDK

执行以下命令卸载已安装的 Agent SDK 包：

```bash
oedp run uninstall
```

**注意：** 卸载操作只会移除 Agent SDK 相关的 pip 包，不会卸载 python3 和 pip 本身。

### 4. 本地部署测试

可以使用 `-lt` 参数在本地快速测试：

```bash
oedp run install -lt
```

## 使用示例

### 示例 1：安装 LangChain（默认）

```yaml
# config.yaml
vars:
  agent_sdk: langchain
```

```bash
oedp run install
```

### 示例 2：安装 PyAutoGen

```yaml
# config.yaml
vars:
  agent_sdk: pyautogen
```

```bash
oedp run install
```

### 示例 3：安装 CrewAI

```yaml
# config.yaml
vars:
  agent_sdk: crewai
```

```bash
oedp run install
```

### 示例 4：切换 Agent SDK

如果需要切换到其他 Agent SDK，只需：
1. 卸载当前的 SDK：`oedp run uninstall`
2. 修改 `config.yaml` 中的 `agent_sdk` 配置
3. 安装新的 SDK：`oedp run install`

## 安装验证

每次安装完成后，插件会自动运行一个小型演示程序来验证安装是否成功。如果看到类似以下输出，说明安装成功：

```
=== LangChain Installation Verification ===
Status: SUCCESS
All LangChain core components are working properly!
==========================================
```

## 添加新的 Agent SDK

如果需要支持新的 Agent SDK，只需：

1. 在 `workspace/agent_types.yaml` 中添加配置：
```yaml
agents:
  new_sdk:
    packages:
      - new-sdk-package>=1.0.0
    demo: demos/demo_new_sdk.py
    description: Description of the new SDK
```

2. 在 `workspace/demos/` 目录下创建对应的验证脚本 `demo_new_sdk.py`

3. 在 `config.yaml` 的注释中补充新 SDK 的说明
