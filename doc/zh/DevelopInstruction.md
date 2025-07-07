# oeDeploy 插件开发

## 1 oeDeploy 插件概念介绍

- oeDeploy 插件（plugin）是 oedp 工具中提供自动化部署能力的组件，将复杂的部署流程脚本化来实现自动化部署。
- 一个插件中可能会集成多种部署操作（action），例如安装、卸载、环境清理等。
- 每一个部署操作都会对应一个或多个步骤（task），每个步骤对应一个部署脚本（例如 ansible 的 playbook）。

## 2 oeDeploy 插件目录结构

oeDeploy 插件目录名称，即插件名称，可以包含版本号（表示软件本身的版本，而非插件的版本）

插件目录下包含如下内容：

| 文件或者目录名 | 类型 | 介绍                                                                                                                                                      |
| -------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| config.yaml    | yaml | 对用户暴露的唯一配置文件。包含主机相关的配置，如 ip、密码、密钥、端口号等，还包含了软件部署相关的配置项。                                                 |
| main.yaml      | yaml | 包含了插件的各种信息，例如名称、版本号、描述，也包含了每个部署操作（action）执行时的具体步骤，每个步骤都对应一个脚本或者playbook（以workspace为根目录）。 |
| doc            | 目录 | 承载插件相关的用户文档。该目录非必需。                                                                                                                    |
| workspace      | 目录 | 承载了软件安装部署所使用的所有文件、源码、二进制、脚本、playbook等等。目录内结构不做限制。                                                                |

## 3 `main.yaml`

`main.yaml`主要用于记录插件的关键信息，包括：名称（`name`）、版本（`version`）、插件介绍（`description`）、操作（`action`）等。

- 当用户执行`oedp info`命令时，`oedp`工具会读取并解析该文件，向用户展示相关信息。
- 当用户执行`oedp run xxxx`命令时，`oedp`工具会根据`action`字段中的内容，执行对应的自动化脚本。

### 3.1 `main.yaml`格式说明：

- `action`字段中包含了一个或者多个操作。
- 每一个具体操的key是操作名称，`description` 项是该操作的介绍，`tasks`中承载该操作所需执行的具体步骤（一个列表），当该操作被用户触发，将按顺序执行每一步骤。
- 每一个步骤包含如下几个字段：
  `name`：步骤名称，必填字段。
  `playbook`：表示用`ansible-playbook`执行对应的脚本，内容为 playbook 的路径（基于`workspace`目录的相对路径）。必填字段。目前仅支持`playbook`这一种模式。
  `vars`：脚本执行时所读取的配置文件路径（基于`workspace`目录的相对路径）。非必填字段。
  `scope`：限定了需要执行该步骤的节点，即主机组（在`config.yaml`中定义）。必填字段，通常默认为`all`。
- 当用户执行了命令行`oedp run <action>`，`oedp`工具会按顺序逐一执行这个操作下的所有的步骤（`tasks`）。
- 在`playbook`模式下，每个步骤等价于如下命令行：

```bash
ansible-playbook <playbook>.yaml -i config.yaml -e @<vars>.yaml --limit <scope>
```

### 3.2 `main.yaml`举例说明：

```yaml
name: kubernetes-1.31.1  # 插件名称
version: 1.0.0           # 插件版本号
description: install kubernetes 1.31.1  # 插件描述
action:
  install:                              # 操作install
    description: install kubernetes     # 操作install的描述
    tasks:
      - name: prepare for install       # 操作install的第1个步骤
        playbook: set-env.yml           # 当前步骤所执行的playbook文件（基于workspace目录的相对路径）
        scope: all                      # 执行当前步骤的主机组名称（在config.yaml中定义）
      - name: install kubernetes        # 操作install的第2个步骤
        playbook: init-k8s.yml          # 当前步骤所执行的playbook文件（基于workspace目录的相对路径）
        vars: variables.yml             # 当前步骤所读取的配置文件（基于workspace目录的相对路径）
        scope: all                      # 执行当前步骤的主机组名称（在config.yaml中定义）
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

- 在这个示例中，当用户执行了 `oedp run install` 命令，工具会按顺序执行如下命令：
  `ansible-playbook set-env.yml -i config.yaml --limit all`
  `ansible-playbook init-k8s.yml -i config.yaml -e @variables.yml --limit all`
- 用户可以通过`oedp run install`、`oedp run delete`、`oedp run clean`命令行来触发对应的操作。

## 4 `config.yaml`

部署脚本在执行过程中的可调整参数都在同一个配置文件`config.yaml`中承载，降低使用者的学习成本和开发者的维护成本。

- `config.yaml`包含部署环境的节点信息（主机组），以及部署软件相关的参数配置。
- `config.yaml`遵循 ansible 的 inventory 文件配置规则，工具在执行 ansible playbook 时直接作为 inventory 传入。
- 需要注意，`config.yaml`是对普通用户暴露的唯一配置文件，应当注意美观，避免歧义，并保留尽可能详细的注释说明。
- 在`playbook`模式下，通过如下命令行的方式导入`config.yaml`中的配置：

```bash
ansible-playbook <playbook>.yaml -i config.yaml -e @<vars>.yaml --limit <scope>
```

### 4.1 `config.yaml`示例1：本地部署

```yaml
all:
  hosts:
    localhost:
      ansible_connection: local
  vars:
    deepseek_version: 8b
    ollama_download_url:
      amd64: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/ollama-linux-amd64.tgz
      arm64: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/ollama-linux-arm64.tgz
    ollama_download_path: /root/tmp     # 下载的目标路径
    modelfile_download: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
    modelfile_download_path: /root/tmp  # 下载的目标路径
    # 模型参数
    parameter:
      temperature: 0.7
      top_p: 0.7
      top_k: 30
      num_ctx: 4096
      num_thread: 4    # 线程数，建议不超过CPU核数
      num_gpu: 0       # GPU数  0 for none, -1 for all.
    download_checksum: true        # 是否打开sha256sum校验
    download_timeout: 600          # 下载大文件时的超时时间(秒)
    download_retry: 6              # 下载大文件重试次数
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
```

### 4.2 `config.yaml`示例2：单节点部署

```yaml
all:
  hosts:
    host1:
      ansible_host: 127.0.0.1      # 远端IP
      ansible_port: 22             # 端口号
      ansible_user: root           # 用户名
      ansible_password: ""   # 密码
  vars:
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'

    kubectl_apply: pytorch-deployment.yaml
    namespace: pytorch-namespace
    replicas: 1
    containers:
      http:
        name: http-container
        image: hub.oepkgs.net/oedeploy/pytorch/pytorch:latest  # amd64
      workspace_mount: /tmp
    service:
      port: 8080
      target_port: 8080
      node_port: 30699
    training:
      epoch: 2   # 训练轮数
```

### 4.3 `config.yaml`示例3：多节点部署

```yaml
all:
  hosts:
    host1:
      ansible_host: 192.168.1.101
      ansible_port: 22
      ansible_user: root
      ansible_password: ""
      architecture: amd64          # e.g. [ amd64, arm64 ]
    host2:
      ansible_host: 192.168.1.102
      ansible_port: 22
      ansible_user: root
      ansible_password: ""
      architecture: amd64          # e.g. [ amd64, arm64 ]
  vars:
    version: 3.9.0
    download_url: https://get.helm.sh/
    temp_path: /tmp
    install_path: /usr/local/bin
    force_install: yes
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
```

### 4.4 `config.yaml`示例4：多节点分组部署

```yaml
all:
  children:
    masters:
      hosts:
        HOST1:                             # e.g. 192.168.10.1
          ansible_host: 192.168.10.1       # e.g. 192.168.10.1
          ansible_port: 22
          ansible_user: root
          ansible_password: ""
          architecture: amd64              # e.g. [ amd64, arm64 ]
          oeversion: 24.03-LTS             # e.g. [ 22.03-LTS, 24.03-LTS ]
          runtime: docker                  # e.g. [ docker, containerd ]
    workers:
      hosts:
        HOST2:
          ansible_host: 192.168.10.2
          ansible_port: 22
          ansible_user: root
          ansible_password: ""
          architecture: amd64
          oeversion: 24.03-LTS
          runtime: docker
        HOST3:
          ansible_host: 192.168.10.3
          ansible_port: 22
          ansible_user: root
          ansible_password: ""
          architecture: amd64
          oeversion: 24.03-LTS
          runtime: docker
    new-workers:  # new-workers字段不可删除
      hosts:
  vars:
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'

    init_cluster_force: "true"             # e.g. [ "true", "false" ]  强制初始化集群
    remove_master_no_schedule_taints: "true"
    service_cidr: 10.96.0.0/16             # 服务网段
    pod_cidr: 10.244.0.0/16                # pod ip 网段
    certs_expired: 3650                    # 证书过期时间
    # lb_kube_apiserver_ip:
    lb_kube_apiserver_port: 8443
    has_deployed_containerd: "false"       # e.g. [ "true", "false" ]  是否已有 containerd

    # 以下参数需要与build过程中的host.ini保持一致，如果不涉及请忽视
    kubernetes_version: 1.31.1
    calico_version: 3.28.2
    pause_image: "registry.k8s.io/pause:3.10"
```

## 5 `workspace`目录

`workspace`目录中承载了部署脚本的主体内容，目录结构不做限制。

- `main.yaml`和 `config.yaml`涉及的各种文件、源码、二进制、脚本、playbook，都在`workspace`目录中承载，开发者可自定义其中的子目录。

- `workspace`目录视为整个插件执行过程的根目录。

### 5.1 `workspace`示例

这里有一个用于部署nginx服务的 oeDeploy 插件

`config.yaml`内容如下：

```yaml
name: nginx
version: 1.25.3
description: Install and configure nginx web server
action:
  install:
    description: Install nginx and start service
    tasks:
      - name: Install nginx via yum
        playbook: install.yml
      - name: Configure and start nginx
        playbook: configure.yml
```

`config.yaml`的内容如下：

```yaml
all:
  hosts:
    127.0.0.1:
      ansible_host: 127.0.0.1
      ansible_port: 22
      ansible_user: root # 必须为root用户
      ansible_password: ""
  vars:
    nginx_port: 80
    ansible_ssh_common_args: "-o StrictHostKeyChecking=no"
```

`workspace`目录下包含如下文件：

1. `install.yml`：用于安装nginx及其他依赖软件
2. `configure.yml`：用于配置nginx参数并启动nginx服务
3. `nginx.conf.j2`：作为配置nginx参数的模板。虽然未在`config.yaml`中体现，但会在`configure.yml`中被使用。

`install.yml`的内容如下：

```yaml
---
- hosts: all
  become: yes
  tasks:
    - name: Install nginx
      yum:
        name: nginx
        state: present
    - name: Ensure nginx is running and enabled
      service:
        name: nginx
        state: started
        enabled: yes
```

`configure.yml`的内容如下：

```yaml
---
- hosts: all
  become: yes
  tasks:
    - name: Generate nginx configuration
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        owner: root
        group: root
        mode: '0644'
    - name: Validate nginx configuration
      command: nginx -t
      register: nginx_test
      changed_when: false
      notify: restart nginx
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
      when: nginx_test.rc == 0
```

`nginx.conf.j2`的内容如下：

```jinja2
worker_processes auto;
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    server {
        listen       {{ nginx_port }};
        server_name  localhost;

        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
        }

        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   /usr/share/nginx/html;
        }
    }
}
```

## 6 插件打包

如果要发布插件供其他用户使用，需要将插件打包成`{plugin_name}.tar.gz`的格式，压缩包的名称与插件名称保持一致，且解压后应当仅生成一个目录，例如：

```text
kubernetes-1.31.1.tar.gz
`-- kubernetes-1.31.1
    |-- main.yaml 
    |-- config.yaml
    `-- workspace/
```

通常可以使用如下命令行完成打包：

```bash
tar zcvf kubernetes-1.31.1.tar.gz kubernetes-1.31.1/
```

## 7 插件开发Tips

- 如果 ansible 脚本中涉及文件的跨节点拷贝，建议在拷贝之前，在目标节点上安装软件包`python3-libselinux`
- 为了部署的流畅性，建议在`config.yaml`中的`vars`字段增加配置项`ansible_ssh_common_args: '-o StrictHostKeyChecking=no'`，从而关闭严格的 HostKey 校验。
