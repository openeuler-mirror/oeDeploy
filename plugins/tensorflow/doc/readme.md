# 使用 oeDeploy 基于 k8s 集群部署TensorFlow



1. 准备一个k8s集群

2. 下载oedp命令行工具，并用yum安装。如有更新的oedp版本，可以选择新版本。

   ````bash
   # x86_64:
   wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/x86_64/Packages/oedp-1.0.0-20250208.x86_64.rpm
   yum install -y oedp-1.0.0-20250208.x86_64.rpm
   # aarch64:
   wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/aarch64/Packages/oedp-1.0.0-20250208.aarch64.rpm
   yum install -y oedp-1.0.0-20250208.aarch64.rpm
   ````

3. 根据实际情况，修改config.yaml
   请确保目标节点为k8s的master节点
   `kubectl_apply`需要与workspace下的playbook对应。

4. 一键部署
   ````bash
   oedp run install -p tensorflow  # -p <插件目录>
   ````

5. 一键卸载
   ````bash
   oedp run uninstall -p tensorflow  # -p <插件目录>
   ````

   

# demo

## demo 1: tensorflow with jupyter

- config.yaml
  ````yaml
  all:
    hosts:
      localhost:
        ansible_connection: local
    
    vars:
      ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
  
      kubectl_apply: tensorflow-deployment.yaml
      namespace: tensorflow-namespace
      replicas: 1
      containers:
        name: tensorflow-jupyter
        image: hub.oepkgs.net/oedeploy/tensorflow/tensorflow:latest-jupyter  # amd64 only
        command: ["jupyter", "notebook", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
      service:
        name: tensorflow-service
        port: 80
        target_port: 8888
        node_port: 30088
  ````
  
- 查看pod状态

    ````bash
    kubectl get pods -n tensorflow-namespace
    ````

    ````
    NAME                                             READY   STATUS    RESTARTS   AGE
    tensorflow-deployment-75b85948d8-w2n7b           1/1     Running   0          4m1s
    ````

- 进入pod容器，会有一个很明显的TensorFlow大字提示

    ````bash
    kubectl exec -n tensorflow-namespace -it tensorflow-deployment-75b85948d8-w2n7b -- /bin/bash
    ````

- 打印TensorFlow信息

    ````bash
    python -c "import tensorflow as tf; print(tf.__version__)"
    ````

- 打开jupyter界面

    ````bash
    http://x.x.x.x:30088/  # master所在节点
    ````



## demo 2: 分布式部署训练集群

- config.yaml
  ````yaml
  all:
    hosts:
      localhost:
        ansible_connection: local
    
    vars:
      ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
      
      kubectl_apply: tensorflow-distributed.yaml
      namespace: tensorflow-namespace
      ps:
        replicas: 2
        containers:
          name: tensorflow-ps
          image: hub.oepkgs.net/oedeploy/tensorflow/tensorflow:latest  # amd64 only
        service:
          name: tensorflow-ps-service
          port: 2222
          target_port: 2222
      worker:
        replicas: 2
        containers:
          name: tensorflow-worker
          image: hub.oepkgs.net/oedeploy/tensorflow/tensorflow:latest  # amd64 only
        service:
          name: tensorflow-worker-service
          port: 2222
          target_port: 2222
  ````
  
  - 查看pod状态

  ````bash
  kubectl get pods -n tensorflow-namespace
  ````
  
  ````
  NAME                                 READY   STATUS    RESTARTS   AGE
  tensorflow-ps-fdddfdb5f-8fc98        1/1     Running   0          2m59s
  tensorflow-ps-fdddfdb5f-dgqm9        1/1     Running   0          2m59s
  tensorflow-worker-6cd8947b75-gxcnq   1/1     Running   0          2m59s
  tensorflow-worker-6cd8947b75-wbt57   1/1     Running   0          2m59s
  ````

  ````bash
  kubectl logs tensorflow-ps-fdddfdb5f-8fc98 -n tensorflow-namespace
  ````
  
  ````
  2025-02-07 09:25:24.882206: I tensorflow/core/util/port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
  2025-02-07 09:25:24.915813: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
  To enable the following instructions: AVX2 AVX512F AVX512_VNNI FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
  TensorFlow version: 2.18.0
  Environment variables: environ({'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'tensorflow-ps-fdddfdb5f-8fc98', 'DEBIAN_FRONTEND': 'noninteractive', 'LANG': 'C.UTF-8', 'TF_CONFIG': '{\n  "cluster": {\n    "ps": ["tensorflow-ps:2222"],\n    "worker": ["tensorflow-worker-0:2222", "tensorflow-worker-1:2222"]\n  },\n  "task": {"type": "ps", "index": 0}\n}\n', 'KUBERNETES_PORT_443_TCP_PROTO': 'tcp', 'TENSORFLOW_PS_PORT_2222_TCP_PROTO': 'tcp', 'TENSORFLOW_WORKER_SERVICE_PORT': '2222', 'TENSORFLOW_WORKER_PORT': 'tcp://10.96.56.106:2222', 'KUBERNETES_SERVICE_HOST': '10.96.0.1', 'KUBERNETES_PORT_443_TCP_PORT': '443', 'TENSORFLOW_PS_PORT_2222_TCP_PORT': '2222', 'TENSORFLOW_WORKER_PORT_2222_TCP_ADDR': '10.96.56.106', 'TENSORFLOW_WORKER_SERVICE_HOST': '10.96.56.106', 'TENSORFLOW_WORKER_PORT_2222_TCP_PROTO': 'tcp', 'KUBERNETES_SERVICE_PORT': '443', 'KUBERNETES_SERVICE_PORT_HTTPS': '443', 'KUBERNETES_PORT': 'tcp://10.96.0.1:443', 'KUBERNETES_PORT_443_TCP': 'tcp://10.96.0.1:443', 'TENSORFLOW_PS_PORT_2222_TCP': 'tcp://10.96.88.2:2222', 'TENSORFLOW_PS_PORT_2222_TCP_ADDR': '10.96.88.2', 'TENSORFLOW_WORKER_PORT_2222_TCP_PORT': '2222', 'KUBERNETES_PORT_443_TCP_ADDR': '10.96.0.1', 'TENSORFLOW_PS_SERVICE_HOST': '10.96.88.2', 'TENSORFLOW_PS_SERVICE_PORT': '2222', 'TENSORFLOW_PS_PORT': 'tcp://10.96.88.2:2222', 'TENSORFLOW_WORKER_PORT_2222_TCP': 'tcp://10.96.56.106:2222', 'HOME': '/root', 'ENABLE_RUNTIME_UPTIME_TELEMETRY': '1', 'TF2_BEHAVIOR': '1', 'TPU_ML_PLATFORM': 'Tensorflow', 'TPU_ML_PLATFORM_VERSION': '2.18.0'})
  This is the parameter server.
  [2025-02-07 09:25:26.288107] Parameter server is running...
  [2025-02-07 09:26:26.288219] Parameter server is running...
  [2025-02-07 09:27:26.288358] Parameter server is running...
  [2025-02-07 09:28:26.288519] Parameter server is running...
  ````
  
  - 卸载pod

  ````bash
  kubectl delete -f tensorflow-distributed.yaml
  ````
  
  

