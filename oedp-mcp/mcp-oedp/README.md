# oeDeploy MCP Server `mcp-oedp` 使用说明

该 MCP Server 用于帮助用户智能调用 oeDeploy 相关能力实现软件快速部署。

## 1. 环境准备

下载 oeDeploy 代码，将`oeDeploy/oedp-mcp/mcp-oedp`目录拷贝到自定义路径，例如`~/.oedp/mcp/`

```bash
git clone https://gitee.com/openeuler/oeDeploy.git
mkdir -p ~/.oedp/mcp/
cp -r oeDeploy/oedp-mcp/mcp-oedp ~/.oedp/mcp/
```

配置 python 虚环境，进入`mcp-oedp`目录，完成`uv`初始化并安装依赖。

```bash
cd ~/.oedp/mcp/mcp-oedp
uv venv --system-site-packages
uv pip install -e .
```

## 2. MCP 配置

请确保你的智能体应用（交互界面）支持 MCP 服务，例如 Roo Code 和 Cherry Studio。

打开 MCP 配置页面进行手动配置，或直接编辑 MCP 配置文件。这里需要用户配置大模型 API 的访问地址`model_url`、秘钥`api_key`、模型名称`model_name`，用于 MCP Server 内处理相对复杂的操作。如果大模型的 API 不可用，会导致 MCP Server 初始化失败。相关信息可以从 DeepSeek、硅基流动等模型服务提供商的官网获取。

例如，使用 DeepSeek 官方的 API，可参考如下配置：

````json
{
  "mcpServers": {
    "mcp-oedp": {
      "command": "uv",
      "args": [
        "--directory", ".oedp/mcp/mcp-oedp",
        "run", "mcp-oedp.py",
        "--model_url", "https://api.deepseek.com",
        "--api_key", "<your key of deepseek api>",
        "--model_name", "deepseek-chat"
      ],
      "disabled": false,
      "timeout": 1800
    }
  }
}
````

配置完成后，可以在 MCP 列表上看看到`mcp-oedp`，且状态正常。

> 如果 MCP Server 状态异常，请根据提示信息检查 python 组件依赖是否满足。

## 3. 自然语言实现一键部署

接下来我们让 AI 帮我们完成 kubernetes-1.31.1 的一键部署。请提前准备3个linux节点，三层网络互通。

Roo Code 中新建对话框，发送如下指令：

```
用oeDeploy一键部署kubernetes-1.31.1
master节点ip为192.168.0.10，root密码为xxxxxxxx，架构为amd64，oe版本为24.03-LTS
第1个worker节点ip为192.168.0.11，root密码为xxxxxxxx，架构为amd64，oe版本为24.03-LTS
第2个worker节点ip为192.168.0.12，root密码为xxxxxxxx，架构为amd64，oe版本为24.03-LTS
```

MCP 会让大模型自动帮我们完成 oeDeploy 插件的初始化、参数配置，以及最终的部署操作。
