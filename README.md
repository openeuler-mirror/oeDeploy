# oeDeploy 用户指南

## 1 工具介绍

### 1.1 oeDeploy简介

oeDeploy（简称oedp）作为应用快速安装部署平台，将提供如下能力：

1. 插件库：实现应用快速安装的基础，应用提供部署的基本能力就可按照基本规范进行oedp 插件化改造，oedp本身对插件的能力进行解析和调度执行
2. 应用碎片化部署能力自动ansible化改造：针对不具备自动化安装的应用，指定安装步骤进行配置，oedp工具解析，自动转换成ansible playbook配置
3. 应用一键安装能力集成：支持具备一键脚本安装部署/ansible自动化安装部署的快速插件集成
4. 分发能力：oedp支持应用部署在对应host上的的一键分发
5. ansible集成： 目前oedp的一些基础能力基于ansible进行改造

### 1.2 工具组成

oedp工具由以下三部分组成：

+ oedp Web UI：**(待实现)** Web UI 旨在简化用户操作流程，降低用户（尤其是初学者）的学习成本，快速、高效地使用 oedp 工具。Web UI 基于命令行工具，通过将用户的配置转化为对应的命令行来完成部署任务。
+ oedp 命令行工具：命令行工具本身不直接提供实际部署功能，而是作为一个集成、分发的平台，调起插件的部署功能，并向用户或UI进行反馈。对于高阶使用者，可以使用命令行工具来直接完成部署任务，相较于使用 Web UI，能够实现更加定制化的操作。
+ oedp 插件：插件用于提供原子化的自动化部署能力，并提供操作接口，分别实现不同的部署操作，例如安装、卸载、环境清理等。

### 1.3 获取与安装

用户可以自主获取 oedp 工具，支持x86_64和aarch64架构。

获取 oedp 工具后，使用 yum/dnf 进行安装：`yum install -y oedp-xxx.rpm`。

### 1.4 命令列表

+ `oedp init <plugin>`：初始化一个插件
    + `-p|--project <path>`：必须，指定初始化路径
    + `-l|--local <path>`：可选，指定一个路径为本地源
    + `-f|--force`：可选，强制覆盖路径，如果路径存在，会先删除其中的所有文件再初始化
+ `oedp list`：列举有哪些可用的插件
    + `-l|--local <path>`：可选，指定一个路径为本地源
+ `oedp info`：查看一个项目的详细信息
    + `-p|--project <path>`：可选，指定一个项目，如果没有指定就使用当前路径
+ `oedp run <action>`：执行一个项目的方法
    + `<action>`：插件可使用的方法名称，可通过`oedp info`命令查询获得
    + `-p|--project <path>`：可选，指定一个项目，如果没有指定就使用当前路径
+ `oedp check`：**(待实现)** 检查一个项目
    + `-p|--project <path>`：可选，指定一个项目，如果没有指定就使用当前路径

### 1.5 工具文件路径

+ `/var/oedp/log/`：日志文件路径
+ `/var/oedp/plugin/`：插件缓存路径
+ `/usr/lib/oedp/src/`：源码路径
+ `/etc/oedp/config`：配置文件路径

## 2 用户部署指南

下面以自动化部署kubernetes-1.31.1为例，讲解部署流程：

### 2.1 获取部署插件

执行以下命令，获取并解压插件包，确保当前目录下出现了目录`kubernetes-1.31.1/`。

```shell
wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/kubernetes-1.31.1.tar.gz
tar -zxvf kubernetes-1.31.1.tar.gz
```

### 2.2 查看插件详细信息

执行`info`命令以查看插件详细信息：

```shell
oedp info -p kubernetes-1.31.1
```

### 2.3 配置节点信息

修改项目配置文件，根据实际情况配置节点信息：

```shell
vim kubernetes-1.31.1/config.yaml
```

注意：

+ 主机ssh配置支持密码登录和密钥登录两种方式，如果使用密钥登录，则不需要配置密码。
+ 无论使用哪种方式进行ssh连接，都需要确保控制节点可用ssh访问目标主机，并确保所有目标主机都加入了控制节点的`known_hosts`中（可以通过手动ssh连接一次每一台目标主机来实现）。

### 2.4 执行部署

执行以下命令以开始自动化部署：

```shell
oedp run install -p kubernetes-1.31.1
```

执行以下命令以卸载k8s：

```shell
oedp run delete -p kubernetes-1.31.1
```

## 3 插件开发指南

### 3.1 oedp 插件介绍

oedp 插件（plugin）是 oedp 工具中提供自动化部署能力的组件，通过将复杂的部署流程 ansible 化来实现自动化部署。插件中可能会集成多种部署操作（action），例如安装、卸载、环境清理等，每一个部署操作都会对应一个 ansible playbook。插件的所有可配置项都应当集中配置，以降低使用者的学习成本和开发者的维护成本。

### 3.2 目录结构

插件开发者在开发插件时应当遵循以下目录结构：

```
{plugin_name}
|-- main.yaml 
|-- config.yaml
`-- workspace/
```

| 文件或者目录名     | 介绍                                                   |
|-------------|------------------------------------------------------|
| config.yaml | 包含主机相关的配置，如ip、密码、密钥、端口号等，还包含了应用的一些部署相关的配置，支持jinja2语言 |
| main.yaml   | oedp识别应用部署流程的主配置文件                                   |
| workspace   | 应用的部署能力库                                             |

其中，`plugin_name`有以下约束：

+ 该插件部署的软件名称为`name`，版本为`version`。
+ `plugin_name`必须是以下两种之一：
  + `{name}-{version}`
  + `{name}-{version}-xxx`
+ 例如，一个插件用于部署kubernetes软件，版本为1.31.1，那么该插件的名称可以是：`kubernetes-1.31.1`，`kubernetes-1.31.1-20240101`，`kubernetes-1.31.1-offline-20240101`等。

下面以kubernetes-1.31.1部署插件为例，简单介绍yaml文件的内容：

#### 3.2.1 main.yaml

`main.yaml`主要用于记录插件的关键信息，包括：名称（name）、版本（version）、介绍（description）、操作（action）等，当用户执行`oedp info`命令时，oedp工具会读取并解析该文件，然后向用户展示其详细信息。

在`action`项中，应当是一个字典（key-value map），每一个 key 将作为操作的名称，对应的 value 中记录了该操作的详情。

操作详情是一个字典，其中的`description`项是该操作的说明，用于在执行`oedp info`命令时向用户展示，而`tasks`项中则记录该操作的具体步骤，为一个列表，执行该操作时，将按顺序执行每一项步骤。

在步骤中，开发者应当指定该步骤需要执行的`playbook`的路径，如果有需要，也可以在`vars`中指定变量文件的路径。所有路径都是相对`workspace`的相对路径。此外，可以指定`scope`，即该步骤需要执行的主机组，默认为`all`。

```yaml
name: kubernetes
version: 1.31.1
description: install kubernetes 1.31.1
action:
  install:
    description: install kubernetes
    tasks:
      - name: install kubernetes
        playbook: init-k8s.yml
        vars: variables.yml
        scope: all
  delete:
    description: delete kubernetes
    tasks:
      - name: delete kubernetes
        playbook: delete-k8s.yml
        vars: variables.yml
        scope: all
  clean:
    description: clean cache files
    tasks:
      - name: clean cache files
        playbook: clean-k8s.yml
        scope: all
```

上述插件中，`workspace/`中的目录结构为：

```
workspace
|-- roles
|   `-- ...
|-- init-k8s.yml
|-- delete-k8s.yml
|-- clean-k8s.yml
|-- variables.yml
`-- ...
```

#### 3.2.2 config.yaml

`config.yaml`是插件中的用户配置文件，主要包含对主机组的配置和一些其他的全局配置，遵循 ansible 的 inventory 文件配置规则，在执行 ansible playbook 时可直接作为 inventory 传入。

插件开发者在开发插件时应注意，要将所有的配置项集中在该文件中进行配置。

```yaml
all:
  children:
    masters:
      hosts:
        Master1:
          ansible_host: 192.168.10.1
          ansible_port: 22
          ansible_user: root
          ansible_password: password
          architecture: amd64
          oeversion: 24.03-LTS
    workers:
      hosts:
        Worker1:
          ansible_host: 192.168.10.2
          ansible_port: 22
          ansible_user: root
          architecture: arm64
          oeversion: 22.03-LTS
        Worker2:
          ansible_host: 192.168.10.3
          ansible_port: 22
          ansible_user: root
          architecture: amd64
          oeversion: 22.03-LTS
  vars:
    init_cluster_force: "true"
    kubernetes_version: 1.31.1
    service_cidr: 10.96.0.0/16
    pod_cidr: 10.244.0.0/16
    pause_image: registry.k8s.io/pause:3.10
    calico_version: 3.28.2
    certs_expired: 3650
    has_deployed_containerd: "false"
```

### 3.3 插件打包

如果要发布插件供用户使用，需要将插件打包成`{plugin_name}.tar.gz`的格式，压缩包的名称和包内目录的名称要对应，且解压后应当仅生成一个目录，例如：

```
kubernetes-1.31.1.tar.gz
`-- kubernetes-1.31.1
    |-- main.yaml 
    |-- config.yaml
    `-- workspace/
```