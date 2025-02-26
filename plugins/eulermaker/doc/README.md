# EulerMaker 自动化部署插件 配置说明

## 1. 主机清单

- **服务节点（ebs control-plane）**：至少1台
    - **架构**：x86_64 或 aarch64（推荐aarch64）
    - **CPU**：>= 64U
    - **内存**：>= 128GB
    - **系统盘**：>= 100G
    - **硬盘**：>= 1T （由于需要存放构建结果，建议硬盘越大越好）
    - **目录**：`/srv/es` `/srv/redis` `/srv/etcd` 单独挂磁盘 （磁盘类型SSD，最好每个单独挂1T，少量构建的可以共用1块磁盘）
    - **开放端口访问**：30108
- **构建节点（ebs testbox）**：每种架构至少1台（用于创建docker构建容器，负责软件包、镜像构建及上传；建议 >= 4台）
    - **架构**：x86_64 >= 1台，aarch64 >= 1台
    - **CPU**：>= 32U（规格越大越好）
    - **内存**：>= 128G（规格越大越好）
- **软件要求**：
    - **操作系统**：openEuler22.03-LTS及以上
    - **git**：2.33.0（建议）
    - **网络**：最好可以访问互联网

| 主机名           | IP地址示例        | 架构    | 系统版本                | 运行时    | 角色类型     | 资源需求    |
|---------------|---------------|-------|---------------------|--------|----------|---------|
| ebs-master-1  | 192.168.1.101 | amd64 | openEuler-22.03-LTS | docker | 主节点/管理面  | 64U128G |
| ebs-master-2  | 192.168.1.102 | amd64 | openEuler-22.03-LTS | docker | 工作节点/管理面 | 32U128G |
| x86-testbox-1 | 192.168.1.201 | amd64 | openEuler-22.03-LTS | docker | 工作节点/执行机 | 32U128G |
| arm-testbox-1 | 192.168.1.202 | arm64 | openEuler-22.03-LTS | docker | 工作节点/执行机 | 32U128G |

> IP地址为示例配置，实际使用需替换为真实环境地址
> 以上机器需要有 root 权限，需要在同一网段，可以相互 ssh 访问。
> - 单架构环境：至少准备2台机器，1台服务节点，1台构建节点。
> - 混合架构环境：至少准备3台机器，1台服务节点，2台构建节点（不同架构）。

## 2. 组结构

```text
all
├── kubernetes
│   ├── masters (控制平面)
│   │   └── ebs-master-1
│   ├── workers (工作节点)
│   │   ├── ebs-master-2
│   │   ├── x86-testbox-1
│   │   └── arm-testbox-1
│   └── new-workers (扩展节点)
└── eulermaker
    ├── kubectl (K8S集群管理节点)
    │   └── ebs-master-1
    ├── masters (EulerMaker管理面)
    │   ├── ebs-master-1
    │   └── ebs-master-2
    ├── testboxs (执行机)
    │   ├── x86-testbox-1
    │   └── arm-testbox-1
    └── new-testboxs (扩展执行机)
```

## 3. 关键变量说明

**Kubernetes 集群配置：**

```yaml
# 网络配置
service_cidr: 10.96.0.0/16
pod_cidr: 10.244.0.0/16

# 组件版本
kubernetes_version: 1.31.1
calico_version: 3.28.2
containerd_version: 1.7.22
docker_version: 27.3.1

# 集群配置
init_cluster_force: true
remove_master_no_schedule_taints: true
certs_expired: 3650
pause_image: registry.k8s.io/pause:3.10
```

**EulerMaker 部署配置：**

```yaml
# 节点配置
es_nodes: [ ebs-master-1, ebs-master-2, ebs-master-1 ]
etcd_nodes: [ ebs-master-1, ebs-master-2, ebs-master-1 ]
redis_nodes: [ ebs-master-1, ebs-master-2 ]×3
rabbitmq_nodes: [ ebs-master-2 ]
ebs_master_nodes: [ ebs-master-1 ]

# 环境配置
yum_repo_is_reachable: true
```

## 4. 注意事项

1. new-workers/new-testboxs 组当前无节点，用于后续扩展
2. 默认配置中，主机信息 password 留空，表示使用 SSH 密钥连接。可根据实际需要改为密码连接。