# oeDeploy MCP Server 使用说明

oeDeploy 目前提供了两个 MCP Server

1. `mcp-oedp`：提供 oedp 基本命令的 MCP 调用
2. `mcp-make-oedp-plugin`：自动完成一个 oeDeploy 插件开发

## 1. 环境准备

安装 python 依赖。为了更加直观，当前示例使用 `pip`安装到系统的 python 目录，实际上更加推荐 `uv`安装到虚拟环境。

````bash
pip install pydantic mcp requests --trusted-host mirrors.huaweicloud.com -i https://mirrors.huaweicloud.com/repository/pypi/simple
````

获取 oeDeploy MCP Server 所需文件。

```bash
mkdir -p ~/.oedp/mcp/
cd ~/.oedp/mcp/
wget https://gitee.com/openeuler/oeDeploy/blob/master/doc/DevelopGuide.md
wget https://gitee.com/openeuler/oeDeploy/blob/master/oedp-mcp/mcp-oedp.py
wget https://gitee.com/openeuler/oeDeploy/blob/master/oedp-mcp/mcp-make-oedp-plugin.py
```

## 2. MCP 配置

当前示例使用 VScode 开发平台，用 Remote ssh 连接到一个 openEuler24.03sp1 的 linux 环境。

在插件 Roo Code中配置了 DeepSeek-V3 的API。

打开 MCP 配置页面，编辑 MCP 配置文件 `mcp_settings.json`，在 `mcpServers`中新增如下内容：

````json
{
  "mcpServers": {

    // ...

    "mcp-oedp": {
      "command": "python3",
      "args": [
        "/root/.oedp/mcp/mcp-oedp.py"
      ],
      "disabled": false,
      "alwaysAllow": []
    },
    "mcp-make-oedp-plugin": {
      "command": "python3",
      "args": [
        "/root/.oedp/mcp/mcp-make-oedp-plugin.py"
      ],
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
````

配置完成后，可以在 MCP 列表上看看到 `mcp-oedp`和 `mcp-make-oedp-plugin`，且状态正常。

> 如果出现报错，请根据提示信息检查 python 组件依赖是否满足。

> 为了提升大模型对 MCP 服务的调用准确度，可以在 Prompt 中补充一句话：
>
> 请仔细阅读我的要求，优先考虑使用MCP解决问题，并选择最匹配的MCP tool函数。如果tool函数返回了一个新的指令字符串，请根据新的指令执行。

## 3. 自动编写一个 oeDeploy 插件

当前示例中，让 AI 帮我们自动写一个 oeDeploy 插件，用于实现 nginx 的软件安装与服务启动。

将如下内容拷贝到 Roo Code 对话框，并发送。为了使结果符合预期，我们应当尽可能准确、详细地描述插件的内容。

````
在~/.oedp/目录下开发一个oeDeploy插件nginx。
插件功能：在单个节点上安装nginx服务并启动。
详细说明：
1. oeDeploy插件配置文件中仅配置单个节点，IP为127.0.0.1，用户名root，密码openEuler@123
2. 当用户执行oedp run install时，在目标节点上，用yum安装nginx，然后启动nginx服务，设置默认启动
3. nginx的端口号(默认80)在oeDeploy插件配置文件中可以配置
````

> 在执行过程中，Roo Code 会多次调用 MCP 或者执行命令行，部分操作会征求用户的许可。我们也可以将这些行为设置为默认允许。

这一过程并不要求我们掌握 oeDeploy 的插件规则，MCP 会让大模型阅读代码仓中的开发文档，并自动完成插件开发。

运行结束后，我们会得到一个 nginx 目录，其中有一些 yaml 文件与脚本，这就是一个可以执行的 oeDeploy 插件。

## 4. 自动实现一键部署

oeDeploy 插件开发完成后，接下来我们让 AI 帮我们完成 nginx 的一键部署。

Roo Code 中新建对话框，发送如下指令：

```
用oeDeploy，在192.168.0.16节点(用户名root，密码openEuler@123)上一键部署nginx
```

> 节点信息请根据实际情况填写，可以是远端地址，也可以是127.0.0.1

MCP 会让大模型自动帮我们完成 oeDeploy 插件的初始化、参数配置，以及最终的部署操作。
