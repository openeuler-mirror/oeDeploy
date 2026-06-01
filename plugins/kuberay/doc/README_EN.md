# KubeRay Deployment Tutorials

## 1. Environment Setup

### 1.1 Deploying a Kubernetes Cluster

Deploy Kubernetes 1.31.1 on the target cluster. In this example, a standard Kubernetes cluster with one master node and two worker nodes is used. The IP address of the master node is 192.168.1.101. You can use the `kubernetes-1.31.1` plug-in for automated deployment.

### 1.2 Installing Helm

Install Helm on the master node. You can use the `helm-3.9.0` plug-in for automated installation.

## 2. Deploying KubeRay

### 2.1 Obtaining the `KubeRay` Plug-in

Run the following command to obtain and initialize the `KubeRay` plug-in.

```shell
oedp repo update
oedp init kuberay
```

### 2.2 Modifying the `config.yaml` File

The following uses the `kuberay/config.yaml` file as an example. Modify the file based on your requirements.

```yaml
all:
  hosts:
    host1:
      ansible_host: 192.168.1.101 # IP address of the master node
      ansible_port: 22                 # SSH port
      ansible_user: root              # SSH user. Non-root users must have the sudo permission.
      ansible_password: ""       # Password of the preceding user
  vars:
    temp_path: /tmp
    namespace: kuberay                 # Namespace
    version: 1.2.2                    # KubeRay chart version

    helm_repo_name: "kuberay"          # Alias of the local Helm repository
    helm_repo_url: "https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/2025.0330/kuberay-helm"

    kuberay_operator_values_file: ""
    # `kuberay_operator_values_file` is an advanced configuration item: Specify a values file for customized configuration.
    # Absolute path for installing the KubeRay operator component. If this parameter is left blank, the following configuration is used:
    kuberay_operator_values:
      repository: "hub.oepkgs.net/oedeploy/quay.io/kuberay/operator" # URL of the KubeRay operator Docker image
      tag: v1.2.2                     # Tag of the KubeRay operator Docker repository

    ray_cluster_values_file: ""
    # `ray_cluster_values_file` is an advanced configuration item: Specify a values file for customized configuration.
    # Absolute path for installing the Ray component. If this parameter is left blank, the following configuration is used:
    ray_cluster_values:
      repository: "hub.oepkgs.net/oedeploy/rayproject/ray-with-pytorch" # URL of the Ray Docker image
      tag: 2.9.0                      # Tag of the Ray Docker repository. When the default Docker source is used, the tag is 2.9.0 for x86 and 2.9.0-aarch64 for Arm. For details about the tag, see the configured repository.
      head:                           # Head node resources
        cpu: "1"
        memory: "2G"
      worker:                         # Worker node resources
        num: 1
        cpu: "1"
        memory: "1G"
    training:                        # Model training parameters
      pip: "https://pypi.tuna.tsinghua.edu.cn/simple"
      batch_size: 1024
      epoch: 5

```

### 2.3 Performing Automatic Deployment

Run the `oedp run install` command in the plugin directory, or run the oedp run the `oedp run install -p [plugin directory]` command in any position to automatically deploy KubeRay.

## 3. Viewing the Dashboard

### 3.1 Querying the Corresponding Port

On the master node, run the `kubectl get svc -A` command to view the port mapping.

````bash
NAMESPACE     NAME                           TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                                                                       AGE
default       kubernetes                     ClusterIP   10.96.0.1       <none>        443/TCP                                                                       24h
kube-system   kube-dns                       ClusterIP   10.96.0.10      <none>        53/UDP,53/TCP,9153/TCP                                                        24h
kuberay       kuberay-operator               ClusterIP   10.96.175.101   <none>        8080/TCP                                                                      9h
kuberay       ray-cluster-kuberay-head-svc   NodePort    10.96.168.232   <none>        10001:32414/TCP,8265:31457/TCP,8080:31582/TCP,6379:31938/TCP,8000:32102/TCP   9h

````shell
The port corresponding to 8265 is the port of the dashboard.

### 3.2 Opening the Dashboard Page
Use the [http://ip:port/] link to open the dashboard page and view information about Ray jobs, serves, clusters, resources, and logs. In the URL, IP indicates the IP address of the master node, and port indicates the port corresponding to 8265 in 3.1.


## Demo 1: Training and Inference of an MLP Model Based on the FashionMNIST Dataset
- KubeRay has been deployed, and the pod resources must be at least 5 vCPUs.
- On the master node, run the following command to perform automatic model training and inference.
    ````bash
    oedp run train -p kuberay
    ````


## Demo 2: Time Comparison Between Running the Same Training Model on a Single Pod and Multiple Pods
Before deploying KubeRay, modify the `config.yaml` file to configure pod resources.
### 1. Set the resources of a single pod as follows.
  ````bash
  head:
    cpu: "7"
    memory: "14G"
  worker:
    num: 0

  ````shell
  Run the following command.
  ````bash
  oedp run install -p kuberay
  oedp run train -p kuberay

  ````shell
### 2. Set the resources of multiple pods as follows.
  ````bash
  head:
    cpu: "7"
    memory: "14G"
  worker:
    num: 2
    cpu: "5"
    memory: "10G"

  ````shell
  Run the following command.
  ````bash
  oedp run install -p kuberay
  oedp run train -p kuberay
  ````shell

### 3. Compare the running time.

In this case, the running time of a single pod is about 25s, and the running time of multiple pods is about 67s.
