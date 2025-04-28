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
      training:                        # 模型训练参数
        pip: "https://pypi.tuna.tsinghua.edu.cn/simple"
        batch_size: 1024
        epoch: 5

```

### 2.2. 执行自动化部署

在插件目录下执行`oedp run install`，或在任意位置执行`oedp run install -p [插件目录]`，即可完成自动化部署 KubeRay。

## 3. 查看 Dashboard

### 3.1. 查询对应端口

在 master 节点，使用`kubectl get svc -A`命令查看端口映射：
````bash
NAMESPACE     NAME                           TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                                                                       AGE
default       kubernetes                     ClusterIP   10.96.0.1       <none>        443/TCP                                                                       24h
kube-system   kube-dns                       ClusterIP   10.96.0.10      <none>        53/UDP,53/TCP,9153/TCP                                                        24h
kuberay       kuberay-operator               ClusterIP   10.96.175.101   <none>        8080/TCP                                                                      9h
kuberay       ray-cluster-kuberay-head-svc   NodePort    10.96.168.232   <none>        10001:32414/TCP,8265:31457/TCP,8080:31582/TCP,6379:31938/TCP,8000:32102/TCP   9h
````
其中 8265 对应的端口，即为 Dashboard 的端口。

### 3.2. 打开 Dashboard 页面
使用 [http://ip:port/] 链接，即可打开 Dashboard 页面，查看 Ray Job / Serve / Cluster 及资源、日志等信息。其中 IP 为 master 节点 IP，port 为 3.1 中 8265 对应的端口。


## Demo: 基于 FashionMNIST 数据集的 MLP 模型训练推理

- 已完成 KubeRay 部署，节点资源要求至少 5U
- 在 master 节点，执行以下命令，即可一键自动完成模型训练、推理
    ````bash
    oedp run train -p kuberay-1.2.2
    ````
  