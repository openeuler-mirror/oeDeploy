# oeDeploy MCP Server `mcp-make-oedp-plugin` Usage Description

The MCP Server helps users quickly develop custom oeDeploy plugins.

## 1. Environment Setup

Download the oeDeploy code and copy the `oeDeploy/oedp-mcp/mcp-make-oedp-plugin` directory to a custom path, for example, `~/.oedp/mcp/`.
Copy the user development guide `doc/en/DevelopInstruction.md` to the `mcp-make-oedp-plugin` directory.

```bash
git clone https://atomgit.com/openeuler/oeDeploy.git
mkdir -p ~/.oedp/mcp/
cp -r oeDeploy/oedp-mcp/mcp-make-oedp-plugin ~/.oedp/mcp/
cp oeDeploy/doc/en/DevelopInstruction.md ~/.oedp/mcp/mcp-make-oedp-plugin
```

Configure the Python virtual environment, go to the `mcp-make-oedp-plugin` directory, initialize `uv`, and install dependencies.

```bash
cd ~/.oedp/mcp/mcp-make-oedp-plugin
uv venv --system-site-packages
uv pip install -e .
```

## 2. MCP Configuration

You are advised to use an agent application (interaction interface) that supports multiple interactions, such as Roo Code.

Open the MCP configuration page for manual configuration, or directly edit the MCP configuration file.

````json
{
  "mcpServers": {
    "mcp-make-oedp-plugin": {
      "command": "uv",
      "args": [
        "--directory",
        ".oedp/mcp/mcp-make-oedp-plugin",
        "run",
        "mcp-make-oedp-plugin.py",
        "--guide_path",
        "~/.oedp/mcp/mcp-make-oedp-plugin/DevelopInstruction.md"
      ],
      "disabled": false,
    }
  }
}
````

> Enter the project directory and user development guide directory based on the site requirements. Absolute paths are recommended.

After the configuration is complete, you can view `mcp-make-oedp-plugin` in the MCP list and its status is normal.

> If the MCP server status is abnormal, check whether the Python component dependencies meet the requirements as prompted.

## 3. Automatically Compiling an oeDeploy Plugin

Copy the following content to the Roo Code dialog box to enable AI to automatically write an oeDeploy plugin for installing the Nginx software and starting the service. To ensure that the result meets expectations, describe the plugin content as accurately and detailed as possible.

````sh
Develop an oeDeploy plugin named nginx in the ~/.oedp/ directory.
Plugin function: Install and start the Nginx service on a single node.
Description:
1. In the oeDeploy plugin configuration file, configure only a single node with the IP address 127.0.0.1, username root, and password xxxxxxxx.
2. When the user runs the oedp run install command, install Nginx using yum on the target node, start the Nginx service, and set it to start by default.
3. The Nginx port number (80 by default) can be configured in the oeDeploy plugin configuration file.
````

> During the execution, Roo Code will call MCP or run commands multiple times, and some operations will require user consent. We can also set these behaviors to be allowed by default.

This process does not require us to master the plugin rules of oeDeploy. Instead, MCP will enable the LLM to read the development documents in the code repository and automatically develop the plugin.

After the execution is complete, we will obtain an Nginx directory containing some YAML files and scripts. This is an executable oeDeploy plugin.

We can use `oedp info -p ~/.oedp/nginx` to query information about the plugin.

After modifying the node information in `~/.oedp/nginx/config.yaml`, you can use `oedp run install -p ~/.oedp/nginx` to trigger the deployment.
