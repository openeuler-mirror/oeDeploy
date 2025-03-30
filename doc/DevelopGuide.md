# oeDeploy 插件开发指南

## 1 oeDeploy 插件介绍

oeDeploy 插件（plugin）是 oedp 工具中提供自动化部署能力的组件，将复杂的部署流程 ansible 化来实现自动化部署。插件中可能会集成多种部署操作（action），例如安装、卸载、环境清理等，每一个部署操作都会对应一个或多个 ansible playbook。插件的所有可配置项都应当集中配置，以降低使用者的学习成本和开发者的维护成本。

## 2 插件目录结构

oeDeploy 插件目录名称，即插件名称，可以包含版本号（表示软件本身的版本，而非插件的版本）

插件目录下包含如下内容：

| 文件或者目录名 | 类型 | 介绍                                                                                                                                                      |
| -------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| config.yaml    | yaml | 对用户暴露的唯一配置文件。包含主机相关的配置，如 ip、密码、密钥、端口号等，还包含了软件部署相关的配置项。                                                 |
| main.yaml      | yaml | 包含了插件的各种信息，例如名称、版本号、描述，也包含了每个部署操作（action）执行时的具体步骤，每个步骤都对应一个脚本或者playbook（以workspace为根目录）。 |
| doc            | 目录 | 承载插件相关的用户文档。该目录非必需。                                                                                                                    |
| workspace      | 目录 | 承载了软件安装部署所使用的所有文件、源码、二进制、脚本、playbook等等。目录内结构不做限制。                                                                |

## 3 main.yaml

`main.yaml`主要用于记录插件的关键信息，包括：名称（`name`）、版本（`version`）、介绍（`description`）、操作（`action`）等，当用户执行 `oedp info` 命令时，`oedp` 工具会读取并解析该文件，然后向用户展示其详细信息。

- `action` 字段是一个字典（key-value map），每一个 key 将作为操作的名称。在下方的案例中，用户可以通过 `oedp run install`、`oedp run delete`、`oedp run clean` 命令行来触发对应的执行步骤（`tasks`）。
- 每一个具体操作中，`description` 项是该操作的说明，用于在执行 `oedp info` 命令时向用户展示；而 `tasks` 项中则记录该操作的具体步骤，为一个列表，执行该操作时，将按顺序执行每一项步骤。
- 在每个步骤中，开发者应当指定该步骤需要执行的 `playbook` 的路径，也可以在 `vars` 中指定变量文件的路径，`vars` 字段不是必需的。这里所填写的路径都是 `workspace` 目录的相对路径。此外，可以指定 `scope`，即该步骤需要执行的主机组，默认为 all。
- 在下方的案例中，当用户执行了 `oedp run install` 命令，工具会按顺序执行如下命令：
  `ansible-playbook set-env.yml -i config.yaml -e variables.yml --limit all`
  `ansible-playbook init-k8s.yml -i config.yaml -e variables.yml --limit all`
  这里的 `config.yaml` 会在下文介绍。

```yaml
name: kubernetes
version: 1.31.1
description: install kubernetes 1.31.1
action:
  install:
    description: install kubernetes
    tasks:
      - name: prepare for install
        playbook: set-env.yml
        scope: all
      - name: install kubernetes
        playbook: init-k8s.yml
        vars: variables.yml
        scope: all
  delete:
    description: delete kubernetes
    tasks:
      - name: delete kubernetes
        playbook: delete-k8s.yml
        scope: all
  clean:
    description: clean cache files
    tasks:
      - name: clean cache files
        playbook: clean-k8s.yml
        scope: all
```

## 4 config.yaml

`config.yaml `是插件中的用户配置文件，主要包含主机组的节点信息，以及部署软件相关的信息，遵循 ansible 的 inventory 文件配置规则，工具在执行 ansible playbook 时直接作为 inventory 传入。

需要注意，`config.yaml` 是对普通用户暴露的唯一配置文件，应当注意美观，避免歧义，并保留适当的注释说明。

```yaml
all:
  children:
    masters:
      hosts:
        172.27.76.114:                    # master node IP
          ansible_host: 172.27.76.114     # master node IP
          ansible_port: 22
          ansible_user: root
          ansible_password: PASSWORD
          architecture: amd64             # amd64 or arm64
          oeversion: 24.03-LTS            # 22.03-LTS or 24.03-LTS
    workers:
      hosts:
        172.27.70.60:                     # worker node IP
          ansible_host: 172.27.70.60      # worker node IP
          ansible_port: 22
          ansible_user: root
          ansible_password: PASSWORD
          architecture: amd64
          oeversion: 24.03-LTS
        172.27.72.90:                     # worker node IP
          ansible_host: 172.27.72.90      # worker node IP
          ansible_port: 22
          ansible_user: root
          ansible_password: PASSWORD
          architecture: amd64
          oeversion: 24.03-LTS
  vars:
    init_cluster_force: "true"
    service_cidr: 10.96.0.0/16
    pod_cidr: 10.244.0.0/16
    certs_expired: 3650
    has_deployed_containerd: "false"
    ansible_ssh_common_args: "-o StrictHostKeyChecking=no"
```

## 5 workspace

`workspace` 目录中承载了部署脚本的主体内容，目录结构不做限制，需要与 `main.yaml `和 `config.yaml `中的各参数对应。

`workspace` 目录视为整个插件执行过程中的根目录。

当前示例中，`workspace`中的目录结构为：

```
workspace
|-- roles
|   `-- ...
|-- clean-k8s.yml
|-- delete-k8s.yml
|-- init-k8s.yml
|-- set-env.yml
|-- variables.yml
`-- ...
```

## 6 插件打包

如果要发布插件供用户使用，需要将插件打包成 `{plugin_name}.tar.gz` 的格式，压缩包的名称和包内目录的名称要对应，且解压后应当仅生成一个目录，例如：

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
