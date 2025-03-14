# KubeRay 部署手册

## 1. 环境准备

### 1.1. 部署 Kubernetes 集群

在目标集群机器上部署 Kubernetes 1.31.1，此处以 1 master + 2 worker 的标准 K8S 集群为例，其中 master 节点的 IP 为 192.168.1.101。可使用`kubernetes-1.31.1`插件进行自动化部署。

### 1.2. 安装 Helm

在 master 节点上安装 Helm，可使用`helm-3.9.0`插件进行自动化安装。

## 2. 部署 KubeRay

### 2.1. 修改`config.yaml`

以下是`config.yaml`的示例，根据实际情况修改此文件：

```yaml
all:
  hosts:
    host1:
      ansible_host: 192.168.1.101      # master 节点的 IP
      ansible_port: 22                 # ssh 的端口
      ansible_user: root               # ssh 的用户，非root用户需要 sudo 权限
      ansible_password: PASSWORD       # 上述用户的密码
  vars:
    temp_path: /tmp
    namespace: kuberay                 # 命名空间
    version: 1.2.2                     # KubeRay chart 的版本

    helm_repo_name: "kuberay"          # 本地 Helm 仓库别名
    helm_repo_url: "https://ray-project.github.io/kuberay-helm" # Helm 仓库 url

    kuberay_operator_values_file: ""
    # 以上配置项 kuberay_operator_values_file 为高级配置：指定一个 values 文件，用于自定义 
    # KubeRay operator 组件的安装。需填写绝对路径，若留空，则采用以下配置：
    kuberay_operator_values:
      repository: "hub.oepkgs.net/oedeploy/quay.io/kuberay/operator" # KubeRay operator docker 镜像 url
      tag: v1.2.2                      # KubeRay operator docker 仓库 tag

    ray_cluster_values_file: ""
    # 以上配置项 ray_cluster_values_file 为高级配置：指定一个 values 文件，用于自定义 
    # Ray 组件的安装。需填写绝对路径，若留空，则采用以下配置：
    ray_cluster_values:
      repository: "m.daocloud.io/docker.io/rayproject/ray" # Ray docker 镜像 url
      tag: 2.9.0                       # Ray docker 仓库 tag
      head:                            # 头节点资源
        cpu: "1"
        memory: "2G"
      worker:                          # 工作节点资源
        num: 1
        cpu: "1"
        memory: "1G"

```

### 2.2. 执行自动化部署

在插件目录下执行`oedp run install`，或在任意位置执行`oedp run install -p [插件目录]`，即可完成自动化部署 KubeRay。
