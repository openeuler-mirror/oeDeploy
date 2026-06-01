# oeDeploy MCP Server `mcp-oedp` Usage Description

The MCP Server helps users intelligently call oeDeploy capabilities to quickly deploy software.

## 1. Environment Setup

Download the oeDeploy code and copy the `oeDeploy/oedp-mcp/mcp-oedp` directory to a custom path, for example, `~/.oedp/mcp/`.

```bash
git clone https://atomgit.com/openeuler/oeDeploy.git
mkdir -p ~/.oedp/mcp/
cp -r oeDeploy/oedp-mcp/mcp-oedp ~/.oedp/mcp/
```

Configure the Python virtual environment, go to the `mcp-oedp` directory, initialize `uv`, and install dependencies.

```bash
cd ~/.oedp/mcp/mcp-oedp
uv venv --system-site-packages
uv pip install -e .
```

## 2. Supported Transmission Protocols

The MCP server supports the following two transmission protocols:

### 2.1 stdio (Default)

It is suitable for integration with local command line tools, such as Roo Code and Cherry Studio.

### 2.2 HTTP

It is suitable for network access and remote calling, allowing access to MCP services through HTTP.

Supported transmission protocols:

- `--transport streamable-http`: Enable the HTTP stream transmission protocol (recommended).
- `--transport http`: Enable the HTTP transmission protocol (backward compatible).
- `--transport sse`: Enable the Server-Sent Events transmission protocol.
- `--transport stdio`: standard input and output transmission (default)

The HTTP transmission mode supports the following parameters:

- `--host`: specifies the listening host address (default: 0.0.0.0).
- `--port`: specifies the listening port (default: 8080).

## 3. MCP Configuration

### 3.1 stdio Transmission Configuration

Ensure that your intelligent agent application (interaction interface) supports the MCP service, such as Roo Code and Cherry Studio.

Open the MCP configuration page for manual configuration, or directly edit the MCP configuration file. You need to configure the access address `model_url`, key `api_key`, and model name `model_name` of the foundation model API for the MCP server to process relatively complex operations. If the LLM API is unavailable, the MCP server initialization will fail. You can obtain related information from the official websites of model service providers such as DeepSeek and SiliconFlow.

For example, if you use the official API of DeepSeek, refer to the following configuration:

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

### 3.2 HTTP Transmission Configuration

For clients that support the HTTP MCP protocol, you can directly access the clients through HTTP:

```bash
# Enable the HTTP streaming transmission mode (recommended).
uv --directory .oedp/mcp/mcp-oedp run mcp-oedp.py \
  --model_url "https://api.deepseek.com" \
  --api_key "<your key>" \
  --model_name "deepseek-chat" \
  --transport streamable-http \
  --host 0.0.0.0 \
  --port 8080

# Alternatively, use the backward compatible HTTP mode.
uv --directory .oedp/mcp/mcp-oedp run mcp-oedp.py \
  --model_url "https://api.deepseek.com" \
  --api_key "<your key>" \
  --model_name "deepseek-chat" \
  --transport http \
  --host 0.0.0.0 \
  --port 8080
```

**Notes:**

- `streamable-http` is the recommended HTTP transfer protocol.
- `http` provides backward compatibility and automatically attempts multiple HTTP implementations.
- Custom host and port configurations may be restricted in some FastMCP versions.

If you encounter HTTP transmission issues, you are advised to:

1. First, try using the `streamable-http` transmission mode.
2. Use the stdio transmission mode for local development.
3. Use a reverse proxy (such as Nginx) to handle custom host/port requirements.

After the configuration is complete, you can view `mcp-oedp` in the MCP list and its status is normal.

> If the MCP server status is abnormal, check whether the Python component dependencies meet the requirements as prompted.

## 4. One-Click Deployment Using Natural Languages

Next, let's use AI to complete one-click deployment of Kubernetes 1.31.1. Prepare three Linux nodes that can communicate with each other at Layer 3.

Create a dialog box in Roo Code and send the following commands:

```sh
Use oeDeploy to deploy kubernetes-1.31.1 in one click.
The IP address of the master node is 192.168.0.10, the root password is *xxxxxxxx*, the architecture is amd64, and the oe version is 24.03-LTS.
The IP address of the first worker node is 192.168.0.11, the root password is *xxxxxxxx*, the architecture is amd64, and the oe version is 24.03-LTS.
The IP address of the second worker node is 192.168.0.12, the root password is *xxxxxxxx*, the architecture is amd64, and the oe version is 24.03-LTS.
```

MCP will enable the LLM to automatically initialize the oeDeploy plugin, configure parameters, and perform the final deployment.
