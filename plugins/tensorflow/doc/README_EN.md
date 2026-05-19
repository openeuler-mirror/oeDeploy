# TensorFlow Deployment Using oeDeploy Based on a Kubernetes Cluster

1. Prepare a Kubernetes cluster.

2. Download the oedp command line tool and install it using yum. If a new oedp version is available, you can use the new version.

   ````bash
   wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.0-3.oe2403sp2.noarch.rpm
   yum install -y oedp-1.1.0-3.oe2403sp2.noarch.rpm
   ````

3. Obtain and initialize the `tensorflow` plug-in.

    ```shell
    oedp repo update
    oedp init tensorflow
    ```

4. Modify `config.yaml` based on site requirements. Ensure that the target node is the master node of Kubernetes. `kubectl_apply` must correspond to the playbook in the workspace.

5. One-click deployment

   ````bash
   oedp run install -p tensorflow  # -p < plug-in directory >
   ````

6. One-click uninstallation

   ````bash
   oedp run uninstall -p tensorflow  # -p < plug-in directory >
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
  
- Query the pod status.

    ````bash
    kubectl get pods -n tensorflow-namespace
    ````

    ````shell
    NAME                                             READY   STATUS    RESTARTS   AGE
    tensorflow-deployment-75b85948d8-w2n7b           1/1     Running   0          4m1s
    ````

- Access the pod container. A message indicating TensorFlow is displayed.

    ````bash
    kubectl exec -n tensorflow-namespace -it tensorflow-deployment-75b85948d8-w2n7b -- /bin/bash
    ````

- Prints TensorFlow information.

    ````bash
    python -c "import tensorflow as tf; print(tf.__version__)"
    ````

- Open the Jupyter page.

    ````bash
    http://x.x.x.x:30088/  # node where the master is located
    ````

## Demo 2: Distributed Deployment of A Training Cluster

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
  
  - Query the pod status.

  ````bash
  kubectl get pods -n tensorflow-namespace
  ````
  
  ````shell
  NAME                                 READY   STATUS    RESTARTS   AGE
  tensorflow-ps-fdddfdb5f-8fc98        1/1     Running   0          2m59s
  tensorflow-ps-fdddfdb5f-dgqm9        1/1     Running   0          2m59s
  tensorflow-worker-6cd8947b75-gxcnq   1/1     Running   0          2m59s
  tensorflow-worker-6cd8947b75-wbt57   1/1     Running   0          2m59s
  ````

  ````bash
  kubectl logs tensorflow-ps-fdddfdb5f-8fc98 -n tensorflow-namespace
  ````
  
  ````shell
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
  
  - Uninstall the pod.

  ````bash
  kubectl delete -f tensorflow-distributed.yaml
  ````
  