

# kubernetes 一键部署操作示例

准备 3 个 2U4G 的虚拟机环境（三层网络互通），使用的 OS 版本为 openEuler 24.03 或 22.03 的任意版本，目标是部署由 1 个 master、2 个 worker 构成的 k8s 集群。

在任意节点上，下载并安装 oeDeploy 的命令行工具 oedp。

````bash
wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.0.2-1.oe2503.noarch.rpm
yum install -y oedp-1.0.2-1.oe2503.noarch.rpm
````

执行以下命令，获取并解压插件包，确保当前目录下出现了目录`kubernetes-1.31.1`。

```shell
wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/kubernetes-1.31.1.tar.gz
tar -zxvf kubernetes-1.31.1.tar.gz
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
        172.27.76.114:                    # master node IP
          ansible_host: 172.27.76.114     # master node IP
          ansible_port: 22
          ansible_user: root
          ansible_password:
          architecture: amd64             # amd64 or arm64
          oeversion: 24.03-LTS            # 22.03-LTS or 24.03-LTS
    workers:
      hosts:
        172.27.70.60:                     # worker node IP
          ansible_host: 172.27.70.60      # worker node IP
          ansible_port: 22
          ansible_user: root
          ansible_password:
          architecture: amd64
          oeversion: 24.03-LTS
        172.27.72.90:
          ansible_host: 172.27.72.90
          ansible_port: 22
          ansible_user: root
          ansible_password:
          architecture: amd64
          oeversion: 24.03-LTS
  vars:
    init_cluster_force: "true"
    service_cidr: 10.96.0.0/16
    pod_cidr: 10.244.0.0/16
    certs_expired: 3650
    has_deployed_containerd: "false"
    ansible_ssh_common_args: "-o StrictHostKeyChecking=no"
````

> 注意：须确保节点间 ssh 可联通，支持密码登录和密钥登录，如果使用密钥登录，则不需要配置密码。

执行以下命令以开始自动化部署：

```shell
oedp run install -p kubernetes-1.31.1
```

执行以下命令以卸载kubernetes：

```shell
oedp run delete -p kubernetes-1.31.1
```

> -p 参数表示解压后的文件目录。如果进入 kubernetes-1.31.1 插件根目录，执行 oedp 命令时无需 -p 参数。
