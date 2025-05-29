# oeDeploy 应用案例

## 应用案例 1：kubernetes 一键部署

准备 3 个 2U4G 的虚拟机环境（三层网络互通），使用的 OS 版本为 openEuler 24.03 或 22.03 的任意版本，目标是部署由 1 个 master、2 个 worker 构成的 k8s 集群。

在任意节点上，下载并安装 oeDeploy 的命令行工具 oedp。

````bash
wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.0.2-1.oe2503.noarch.rpm
yum install -y oedp-1.0.2-1.oe2503.noarch.rpm
````

执行以下命令，获取插件包，确保当前目录下出现了目录`kubernetes-1.31.1`。

```shell
oedp repo update
oedp init kubernetes-1.31.1
```

执行`info`命令以查看插件详细信息：

```shell
oedp info -p kubernetes-1.31.1
```

修改项目配置文件，根据实际情况配置节点信息：

```shell
vim kubernetes-1.31.1/config.yaml
```

````yaml
all:
  children:
    masters:
      hosts:
        # master节点数量须为奇数
        172.27.76.114:                     # master node IP
          ansible_host: 172.27.76.114      # master node IP
          ansible_port: 22
          ansible_user: root
          ansible_password: ""
          architecture: amd64              # [ amd64, arm64 ]
          oeversion: 24.03-LTS             # [ 22.03-LTS, 24.03-LTS ]
          runtime: docker                  # [ docker, containerd ]
    workers:
      hosts:
        172.27.70.60:                      # worker node IP
          ansible_host: 172.27.70.60       # worker node IP
          ansible_port: 22
          ansible_user: root
          ansible_password: ""
          architecture: amd64
          oeversion: 24.03-LTS
          runtime: docker
        172.27.72.90:
          ansible_host: 172.27.72.90
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

````

> 注意：须确保节点间 ssh 可联通，支持密码登录和密钥登录，如果使用密钥登录，则不需要配置密码。

执行以下命令以开始自动化部署：

```shell
oedp run install -p kubernetes-1.31.1
```

执行以下命令以卸载kubernetes：

```shell
oedp run uninstall -p kubernetes-1.31.1
```

> -p 参数表示解压后的文件目录。如果进入 kubernetes-1.31.1 插件根目录，执行 oedp 命令时无需 -p 参数。
