# Dify 插件使用说明

## 1. 准备环境

准备两个节点（三层网络互通），OS 版本为 openEuler 24.03 或 22.03 的任意 LTS 版本，规格大于 2U4G。

## 2. 安装 oedp 

在控制节点上，下载并安装 oeDeploy 的命令行工具`oedp (version >= 1.1.0-2)`。

````bash
wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.0-2.oe2403sp2.noarch.rpm
yum install -y oedp-1.1.0-3.oe2403sp2.noarch.rpm
````

## 3. 获取插件和插件介绍

在控制节点上下载插件 `dify.tar.gz`，然后将其解压。插件的目录结构如下所示：

```
dify
├── config.yaml
├── doc
│   └── readme.md
├── main.yaml
└── workspace
    ├── check-env.yaml
    ├── files
    │   └── openEuler2409.repo
    ├── install-dify.yaml
    ├── install-docker.yaml
    ├── templates
    │   └── daemon.j2
    └── uninstall-dify.yaml
```

我们主要需要关注 `dify/config.yaml` 文件，在运行插件之前，需要确保配置值 `NODE_NAME`、`NODE_IP`、`NODE_PORT`、`NODE_USER`、`NODE_PASSWORD`得到正确的修改。其内容如下：
```yaml
all:
  hosts:
    # 待修改，NODE_NAME 为节点唯一标识。示例值：dify_node
    NODE_NAME:
      # 待修改，NODE_IP 为节点 IP地址。示例值：192.168.10.1
      ansible_host: NODE_IP
      # 待修改，NODE_PORT 为节点端口号。示例值：22
      ansible_port: NODE_PORT
      # 待修改，NODE_USER 为节点用户名。示例值：root
      ansible_user: NODE_USER
      # 待修改，NODE_PASSWORD 为节点密码。
      ansible_password: NODE_PASSWORD
  vars:
    # 目标节点最小配置要求
    # 最小 CPU 核心数
    MIN_CPU: 2
    # 最小内存
    MIN_MEM_GB: 4

    # Docker 镜像加速站
    DOCKER_IMAGE_URL: https://docker.m.daocloud.io

    # Dify 源码目录
    DIFY_CODE_DIR: /opt/dify
    # Dify github 地址
    DIFY_GIT_URL: https://github.com/langgenius/dify.git
    # github 代理
    GITHUB_PROXY: https://gh.idayer.com/

    # 跳过 ssh 校验（如需禁用此功能，请注释以下配置项）
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
```

> **注意**  
> - 如果使用 SSH 密钥对进行认证，并提前将控制节点的公钥加入目标节点的 ~/.ssh/authorized_keys 文件中，则 `NODE_PASSWORD` 替换为空值。
> - 如果使用 `GITHUB_PROXY` 会导致 git clone 代码失败，可以尝试将其设置为空值，然后重试。

同时对如下两个文件进行说明：

- 文件 `dify/workspace/files/openEuler24.09.repo` 提供了 Docker 的安装源，会放置到目标节点的目录 `/etc/yum.repo.d` 下。

- 文件 `dify/workspace/templates/daemon.j2` 为 Docker 的配置文件，会放置到目标节点的目录 `/etc/docker` 下并更名为 `daemon.json`。

## 4. 执行插件

### 4.1 查看插件信息

```bash
oedp info -p ./dify
```

> 选项 `-p` 后面跟插件解压后的目录路径。

输出如下：

```
[ INFO ] - [info_cmd] - name: dify
version: 
description: install and uninstall Dify
action:
+---+-----------+----------------+
| # |   Action  |  Description   |
+---+-----------+----------------+
| 1 |  install  |  Install Dify  |
| 2 | uninstall | Uninstall Dify |
+---+-----------+----------------+
```

> 输出表示 dify 插件有两个操作，分别是安装和卸载 Dify

### 4.2 安装 Dify

```bash
oedp run install -p ./dify
```

### 4.3 卸载 Dify

```bash
oedp run uninstall -p ./dify
```