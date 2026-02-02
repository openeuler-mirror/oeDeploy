# OpenClaw oeDeploy 插件

## 1 插件简介

OpenClaw 是一个运行在本地设备上的个人 AI 助手网关（Gateway），可连接 WhatsApp、Telegram、Slack、Discord、Google Chat、Signal、iMessage、Microsoft Teams、WebChat 等渠道，并提供 Web 控制面与本地工具能力。本插件用于在 openEuler 上自动化部署 OpenClaw Gateway 服务，提供安装、启动、停止和卸载操作。

## 2 功能特性

- 自动安装 Node.js（如需要）
- 自动升级 Node.js 到版本 22（如当前版本低于 22）
- 安装 OpenClaw 最新版本
- 配置 systemd 服务
- 自动配置防火墙规则（如防火墙已启用）
- 支持所有操作的可重入性

## 3 前置要求

- 必须使用 root 用户执行
- 系统：openEuler
- 网络连接（用于下载软件包）

## 4 配置说明

在 `config.yaml` 中可配置以下参数：

- `openclaw_port`: OpenClaw 服务端口，默认值为 18789
- `npm_registry`: npm 镜像源地址，默认为华为云镜像源

## 5 使用方法

进入项目所在目录：

```bash
cd openclaw/
```

### 安装 OpenClaw

```bash
oedp run install
```

安装完成后，**请务必手动执行以下命令完成初始化**：

```bash
openclaw onboard --install-daemon
```

### 启动服务

```bash
oedp run start
```

启动后会自动执行健康检查并显示控制台 URL。

也可以手动执行如下命令，查看控制台 URL，并通过浏览器进行访问。

```bash
openclaw dashboard
```

如果您的服务部署在远端服务器，可以先在本地执行如下命令：

```bash
ssh -N -L 18789:127.0.0.1:18789 root@<远端服务器IP>
```

再通过浏览器访问控制台页面："http://127.0.0.1:18789/?token=xxxxxx"

### 停止服务

```bash
oedp run stop
```

### 卸载 OpenClaw

```bash
oedp run uninstall
```

注意：卸载操作仅移除 OpenClaw 本身，不会卸载 Node.js 和 nvm。

## 6 操作说明

### install 操作

- 安装 Node.js（如未安装）
- 检查 Node.js 版本，如低于 22 则通过 nvm 安装版本 22
- 安装 OpenClaw 全局包
- 创建 systemd 服务文件
- 配置防火墙规则（如防火墙已启用）

### start 操作

- 启动 OpenClaw 服务
- 执行健康检查
- 显示仪表板信息

### stop 操作

- 停止 OpenClaw 服务

### uninstall 操作

- 停止并禁用服务
- 卸载 OpenClaw
- 清理 systemd 服务文件

## 7 注意事项

1. 所有操作都支持可重入，重复执行不会产生副作用
2. 安装完成后必须先执行 `openclaw onboard --install-daemon` 完成初始化才能启动服务，如果此前已经初始化，则可以直接启动服务
3. 如使用 nvm 安装的 Node.js，需要确保环境变量正确加载
4. 防火墙规则仅在防火墙服务运行时才会配置

## 8 故障排查

### 服务无法启动

1. 检查是否已执行 `openclaw onboard --install-daemon`
2. 查看服务日志：`journalctl -u openclaw -f`
3. 检查端口是否被占用：`netstat -tlnp | grep <openclaw_port>`

### Node.js 版本问题

如果 Node.js 版本低于 22，插件会自动通过 nvm 安装版本 22。请确保网络连接正常。

## 版本信息

- 插件版本：1.0.0
- OpenClaw 版本：最新版
- Node.js 要求版本：>= 22

## 9 部署后常用操作（补充）

### 初始化向导

```bash
openclaw onboard --install-daemon
```

### 手动启动网关（调试用）

```bash
openclaw gateway --port <openclaw_port> --verbose
```

### 健康检查与诊断

```bash
openclaw health
openclaw doctor
```

### 查看控制台登录 URL

```bash
openclaw dashboard
```

### 常用交互示例

```bash
# 发送消息
openclaw message send --to +1234567890 --message "Hello from OpenClaw"

# 与助手对话
openclaw agent --message "Ship checklist" --thinking high
```

### 更新与版本通道

```bash
openclaw update --channel stable|beta|dev
```

### 参考文档

- 官网：https://openclaw.ai
- 文档：https://docs.openclaw.ai
- 快速开始：https://docs.openclaw.ai/start/getting-started
