# oeDeploy 插件开发指南

## 1 oedp 插件介绍

oeDeploy 插件（plugin）是 oedp 工具中提供自动化部署能力的组件，通过将复杂的部署流程 ansible 化来实现自动化部署。插件中可能会集成多种部署操作（action），例如安装、卸载、环境清理等，每一个部署操作都会对应一个或多个 ansible playbook。插件的所有可配置项都应当集中配置，以降低使用者的学习成本和开发者的维护成本。

## 2 插件目录结构

插件开发者在开发插件时应当遵循以下目录结构：

```
{ plugin_name }
|-- main.yaml 
|-- config.yaml
|-- doc/
`-- workspace/
```

| 文件或者目录名 | 介绍                                                         |
| -------------- | ------------------------------------------------------------ |
| config.yaml    | 包含主机相关的配置，如 ip、密码、密钥、端口号等，还包含了应用的一些部署相关的配置，支持 jinja2 语法 |
| main.yaml      | oedp 识别应用部署流程的主配置文件                            |
| doc（可选）    | 插件相关的文档目录                                           |
| workspace      | 应用的部署能力库                                             |

其中，`plugin_name`有以下约束：

+ 该插件部署的软件名称为`name`，版本为`version`。
+ `plugin_name`必须是以下两种之一：
  + `{name}-{version}`
  + `{name}-{version}-xxx`
+ 例如，一个插件用于部署 kubernetes 软件，版本为 1.31.1，那么该插件的名称可以是：kubernetes-1.31.1，kubernetes-1.31.1-20240101，kubernetes-1.31.1-offline-20240101 等。

## 3 main.yaml

main.yaml 主要用于记录插件的关键信息，包括：名称（name）、版本（version）、介绍（description）、操作（action）等，当用户执行`oedp info`命令时，oedp 工具会读取并解析该文件，然后向用户展示其详细信息。

在`action`项中，应当是一个字典（key-value map），每一个 key 将作为操作的名称，对应的 value 中记录了该操作的详情。

操作详情是一个字典，其中的`description`项是该操作的说明，用于在执行`oedp info`命令时向用户展示，而`tasks`项中则记录该操作的具体步骤，为一个列表，执行该操作时，将按顺序执行每一项步骤。

在步骤中，开发者应当指定该步骤需要执行的`playbook`的路径，如果有需要，也可以在`vars`中指定变量文件的路径。所有路径都是相对`workspace`的相对路径。此外，可以指定`scope`，即该步骤需要执行的主机组，默认为 all。

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

## 4 config.yaml

config.yaml 是插件中的用户配置文件，主要包含对主机组的配置和一些其他的全局配置，遵循 ansible 的 inventory 文件配置规则，在执行 ansible playbook 时可直接作为 inventory 传入。

```yaml
all:
  children:
    masters:
      hosts:
        HOST_IP1:                          # e.g. 192.168.10.1
          ansible_host: HOST_IP1           # e.g. 192.168.10.1
          ansible_port: 22
          ansible_user: root
          ansible_password: ""
          architecture: amd64              # e.g. [ amd64, arm64 ]
          oeversion: 22.03-LTS             # e.g. [ 22.03-LTS, 24.03-LTS ]
    workers:
      hosts:
        HOST_IP2:
          ansible_host: HOST_IP2
          ansible_port: 22
          ansible_user: root
          ansible_password: ""
          architecture: amd64
          oeversion: 22.03-LTS
        HOST_IP3:
          ansible_host: HOST_IP3
          ansible_port: 22
          ansible_user: root
          ansible_password: ""
          architecture: amd64
          oeversion: 22.03-LTS
  vars:
    init_cluster_force: "true"             # e.g. [ "true", "false" ]  强制初始化集群
    service_cidr: 10.96.0.0/16             # 服务网段
    pod_cidr: 10.244.0.0/16                # pod ip 网段
    certs_expired: 3650                    # 证书过期时间
    has_deployed_containerd: "false"       # e.g. [ "true", "false" ]  是否已有 containerd
```

## 5 workspace

workspace 目录中承载了部署脚本的主体内容，目录结构不做限制，需要与 main.yaml 和 config.yaml 中的各参数对应。

workspace 目录视为整个插件的根目录。

当前示例中，workspace 中的目录结构为：

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

## 6 插件打包

如果要发布插件供用户使用，需要将插件打包成`{plugin_name}.tar.gz`的格式，压缩包的名称和包内目录的名称要对应，且解压后应当仅生成一个目录，例如：

```
kubernetes-1.31.1.tar.gz
`-- kubernetes-1.31.1
    |-- main.yaml 
    |-- config.yaml
    `-- workspace/
```

当前示例中，使用如下命令行完成打包：

````bash
tar zcvf kubernetes-1.31.1.tar.gz kubernetes-1.31.1/
````

