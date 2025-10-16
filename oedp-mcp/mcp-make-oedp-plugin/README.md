# oeDeploy MCP Server `mcp-make-oedp-plugin` 使用说明

该 MCP Server 用于帮助用户快速开发自定义 oeDeploy 插件。

## 1. 环境准备

下载 oeDeploy 代码，将`oeDeploy/oedp-mcp/mcp-make-oedp-plugin`目录拷贝到自定义路径，例如`~/.oedp/mcp/`
并将用户开发指南`doc/zh/DevelopInstruction.md`拷贝到`mcp-make-oedp-plugin`目录

```bash
git clone https://gitee.com/openeuler/oeDeploy.git
mkdir -p ~/.oedp/mcp/
cp -r oeDeploy/oedp-mcp/mcp-make-oedp-plugin ~/.oedp/mcp/
cp oeDeploy/doc/zh/DevelopInstruction.md ~/.oedp/mcp/mcp-make-oedp-plugin
```

配置 python 虚环境，进入`mcp-make-oedp-plugin`目录，完成`uv`初始化并安装依赖。

```bash
cd ~/.oedp/mcp/mcp-make-oedp-plugin
uv venv --system-site-packages
uv pip install -e .
```

## 2. MCP 配置

建议使用具备多次交互功能的智能体应用（交互界面），例如 Roo Code。

打开 MCP 配置页面进行手动配置，或直接编辑 MCP 配置文件。

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

> 请根据实际情况填写项目目录与用户开发指南的目录，推荐填写绝对路径。

配置完成后，可以在 MCP 列表上看看到`mcp-make-oedp-plugin`，且状态正常。

> 如果 MCP Server 状态异常，请根据提示信息检查 python 组件依赖是否满足。

## 3. 自动编写一个 oeDeploy 插件

将如下内容拷贝到 Roo Code 对话框，让 AI 帮我们自动写一个 oeDeploy 插件，用于实现 nginx 的软件安装与服务启动。为了使结果符合预期，我们应当尽可能准确、详细地描述插件的内容。

````
在~/.oedp/目录下开发一个oeDeploy插件nginx。
插件功能：在单个节点上安装nginx服务并启动。
详细说明：
1. oeDeploy插件配置文件中仅配置单个节点，IP为127.0.0.1，用户名root，密码xxxxxxxx
2. 当用户执行oedp run install时，在目标节点上，用yum安装nginx，然后启动nginx服务，设置默认启动
3. nginx的端口号(默认80)在oeDeploy插件配置文件中可以配置
````

> 在执行过程中，Roo Code 会多次调用 MCP 或者执行命令行，部分操作会征求用户的许可。我们也可以将这些行为设置为默认允许。

这一过程并不要求我们掌握 oeDeploy 的插件规则，MCP 会让大模型阅读代码仓中的开发文档，并自动完成插件开发。

运行结束后，我们会得到一个 nginx 目录，其中有一些 yaml 文件与脚本，这就是一个可以执行的 oeDeploy 插件。

我们可以通过`oedp info -p ~/.oedp/nginx`查询插件的相关信息。

修改`~/.oedp/nginx/config.yaml`中的节点信息后，可以通过`oedp run install -p ~/.oedp/nginx`触发部署操作。
