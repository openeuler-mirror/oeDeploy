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
    kuberay_version: 1.2.2             # KubeRay 的版本（注意不是 Ray 的版本）
    helm_repo_name: "kuberay"          # 本地 Helm 仓库别名
    helm_repo_url: "https://ray-project.github.io/kuberay-helm" # Helm 仓库 url
    namespace: kuberay                 # 命名空间
    dashboard_port: 8265               # Dashboard 使用的端口，默认8265
    dashboard_address: 0.0.0.0         # Dashboard 监听的地址，如果只监听本机可改为 localhost

    ray_cluster_values:
      repository: "m.daocloud.io/docker.io/rayproject/ray" # Ray docker 镜像 url
      ray_version: 2.9.0               # Ray 版本
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

注意：默认配置下，由于下载源网络问题，传输可能较慢，受网络状况影响波动较大。

### 2.3. 开启 Dashboard 端口映射

在插件目录下执行`oedp run port-forward`，或在任意位置执行`oedp run port-forward -p [插件目录]`，可以开启 Dashboard 的端口映射服务，随后可访问`http://<master 节点 IP>:<Dashboard 端口>`来访问 Dashboard，例如`http://192.168.1.101:8265`。

注意：若无法访问 Dashboard，可能为以下原因：
1. 下发部署命令并得到成功返回后，自动化部署流程即成功结束，但此时部署工作可能正在节点后台进行，需要进行镜像拉取、安装等多个步骤，若在部署完成之前进行端口映射可能导致失败，可以多次尝试执行上述命令，或在 master 节点上查看 pod 详情以排查问题。
2. 如果是重复部署，可能存在端口未释放问题，重复执行上述命令可能可以解决问题。
3. 若端口被其他程序占用，端口映射会失败，请检查端口使用情况。
