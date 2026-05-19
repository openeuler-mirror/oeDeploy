# How to Configure the EulerMaker Automatic Deployment Plug-in

## 1. Hosts

- **Service node (ebs control-plane)**: one or more
    - **Architecture**: AArch64 (recommended) or x86_64
    - **CPU**: 64 cores or more
    - **Memory**: 128 GB or more
    - **System drive:** 100 GB or more
    - **Data drive**: 1 TB or more (the larger the better, to accommodate build artifacts storage)
    - **Directories**: `/srv/es`, `/srv/redis`, and `/srv/etcd`, each mounted on a dedicated SSD (recommended) of at least 1 TB. For minimal builds, a single shared drive is sufficient.
    - **Port number**: 30108
- **Build nodes (ebs testbox)**: one or more for each architecture (used to create Docker build containers, handling package and image building and uploading; four or more nodes recommended)
    - **Architecture**: x86_64 (one node or more), AArch64 (one node or more)
    - **CPU**: more than 32 cores (the more the better)
    - **Memory**: more than 128 GB (the larger the better)
- **Software**:
    - **OS**: openEuler 22.03 LTS or later
    - **Git**: 2.33.0 (recommended)
    - **Network**: Internet access is preferred.

| Host Name          | Example IP Address       | Architecture   | OS Version               | Runtime   | Role Type    | Resource Requirement   |
|---------------|---------------|-------|---------------------|--------|----------|---------|
| ebs-master-1  | 192.168.1.101 | amd64 | openEuler-22.03-LTS | docker | Master node/Management plane | 64U128G |
| ebs-master-2  | 192.168.1.102 | amd64 | openEuler-22.03-LTS | docker | Worker node/Management plane| 32U128G |
| x86-testbox-1 | 192.168.1.201 | amd64 | openEuler-22.03-LTS | docker | Worker node/Executor| 32U128G |
| arm-testbox-1 | 192.168.1.202 | arm64 | openEuler-22.03-LTS | docker | Worker node/Executor| 32U128G |

> The IP address is an example. Replace it with the actual IP address.
> Root privileges are required for all machines, which must reside on the same subnet and support mutual SSH access.
> 
> - For single-architecture build: Deploy a minimum of one service node and one build node.
> - For mixed-architecture build: Deploy a minimum of one service node and two build nodes of different architectures.

## 2. Group Structure

```text
all
├── kubernetes
│   ├── masters (control plane)
│   │   └── ebs-master-1
│   ├── workers (worker node)
│   │   ├── ebs-master-2
│   │   ├── x86-testbox-1
│   │   └── arm-testbox-1
│ └── new-workers (extended node)
└── eulermaker
    ├── kubectl (node for managing the K8s cluster)
    │   └── ebs-master-1
    ├── masters (EulerMaker management plane)
    │   ├── ebs-master-1
    │   └── ebs-master-2
    ├── testboxs (executor)
    │   ├── x86-testbox-1
    │   └── arm-testbox-1
    └── new-testboxs (extended executor)
```

## 3. **Key Variables**

**Kubernetes cluster configuration**

```yaml
# Network configuration
service_cidr: 10.96.0.0/16
pod_cidr: 10.244.0.0/16

# Component versions
kubernetes_version: 1.31.1
calico_version: 3.28.2
containerd_version: 1.7.22
docker_version: 27.3.1

# Cluster configuration
init_cluster_force: true
remove_master_no_schedule_taints: true
certs_expired: 3650
pause_image: registry.k8s.io/pause:3.10
```

**EulerMaker deployment and configuration**

```yaml
# Node configuration
es_nodes: [ ebs-master-1, ebs-master-2, ebs-master-1 ]
etcd_nodes: [ ebs-master-1, ebs-master-2, ebs-master-1 ]
redis_nodes: [ ebs-master-1, ebs-master-2 ]×3
rabbitmq_nodes: [ ebs-master-2 ]
ebs_master_nodes: [ ebs-master-1 ]

# Environment configuration
yum_repo_is_reachable: true
```

## 4. Precautions

1. The new-workers/new-testboxs group does not have nodes currently and is used for future expansion.
2. In the default configuration, the password field in the host information is left blank, indicating that the SSH key is used for connection. You can change the connection mode to password-based connection as required.
