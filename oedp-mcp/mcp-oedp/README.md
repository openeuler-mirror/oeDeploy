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

## 2. 传输协议支持

MCP Server 支持两种传输协议：

### 2.1 stdio 传输（默认）
适用于本地命令行工具集成，如 Roo Code、Cherry Studio 等。

### 2.2 HTTP 传输
适用于网络访问和远程调用，支持通过 HTTP 协议访问 MCP 服务。

支持的传输协议：
- `--transport streamable-http`: 启用 HTTP 流传输协议（推荐）
- `--transport http`: 启用 HTTP 传输协议（向后兼容）
- `--transport sse`: 启用 Server-Sent Events 传输协议
- `--transport stdio`: 标准输入输出传输（默认）

HTTP 传输模式支持以下参数：
- `--host`: 指定监听主机地址（默认: 0.0.0.0）
- `--port`: 指定监听端口（默认: 8080）

## 3. MCP 配置

### 3.1 stdio 传输配置

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

### 3.2 HTTP 传输配置

对于支持 HTTP MCP 协议的客户端，可以直接通过 HTTP 访问：

```bash
# 启动 HTTP 流传输模式（推荐）
uv --directory .oedp/mcp/mcp-oedp run mcp-oedp.py \
  --model_url "https://api.deepseek.com" \
  --api_key "<your key>" \
  --model_name "deepseek-chat" \
  --transport streamable-http \
  --host 0.0.0.0 \
  --port 8080

# 或者使用向后兼容的 HTTP 模式
uv --directory .oedp/mcp/mcp-oedp run mcp-oedp.py \
  --model_url "https://api.deepseek.com" \
  --api_key "<your key>" \
  --model_name "deepseek-chat" \
  --transport http \
  --host 0.0.0.0 \
  --port 8080
```

**注意**:
- `streamable-http` 是推荐的 HTTP 传输协议
- `http` 提供向后兼容性，会自动尝试多种 HTTP 实现方式
- 自定义主机和端口配置在某些 FastMCP 版本中可能有限制

如果遇到 HTTP 传输问题，建议：

1. 首先尝试使用 `streamable-http` 传输模式
2. 使用 stdio 传输模式进行本地开发
3. 通过反向代理（如 nginx）来处理自定义主机/端口需求

配置完成后，可以在 MCP 列表上看到`mcp-oedp`，且状态正常。

> 如果 MCP Server 状态异常，请根据提示信息检查 python 组件依赖是否满足。

## 4. 自然语言实现一键部署

接下来我们让 AI 帮我们完成 kubernetes-1.31.1 的一键部署。请提前准备3个linux节点，三层网络互通。

Roo Code 中新建对话框，发送如下指令：

```
用oeDeploy一键部署kubernetes-1.31.1
master节点ip为192.168.0.10，root密码为xxxxxxxx，架构为amd64，oe版本为24.03-LTS
第1个worker节点ip为192.168.0.11，root密码为xxxxxxxx，架构为amd64，oe版本为24.03-LTS
第2个worker节点ip为192.168.0.12，root密码为xxxxxxxx，架构为amd64，oe版本为24.03-LTS
```

MCP 会让大模型自动帮我们完成 oeDeploy 插件的初始化、参数配置，以及最终的部署操作。
