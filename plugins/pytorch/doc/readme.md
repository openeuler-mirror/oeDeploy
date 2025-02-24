# 使用 oeDeploy 基于 k8s 集群部署Pytorch


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
   oedp run install -p pytorch  # -p <插件目录>
   ````

5. 一键卸载
   ````bash
   oedp run uninstall -p pytorch  # -p <插件目录>
   ````



## demo

- config.yaml
  ````yaml
  all:
    hosts:
      localhost:
        ansible_connection: local
    vars:
      ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
      # ================ demo1: pytorch with http.server =====================
      kubectl_apply: pytorch-deployment.yaml
      namespace: pytorch-namespace
      replicas: 1
      containers:
        http:
          name: http-container
          image: hub.oepkgs.net/oedeploy/pytorch/pytorch:latest  # amd64
          # image: hub.oepkgs.net/oedeploy/pytorch/torchserve:latest-arm64  # arm64
        workspace_mount: /tmp
      service:
        port: 8080
        target_port: 8080
        node_port: 30699
  ````
  
- 查看pod

    ````bash
    kubectl get pods -n pytorch-namespace
    ````

    ````
    NAME                                 READY   STATUS    RESTARTS   AGE
    pytorch-deployment-db5d59bcb-ptqnp   1/1     Running   0          15m
    ````

- 查看端口映射，并访问

    ````bash
    kubectl get svc -n pytorch-namespace
    ````

    ````
    NAME              TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
    pytorch-service   NodePort   10.96.50.156   <none>        80:30699/TCP   15m
    ````

    ````
    http://x.x.x.x:30699/  # master所在节点
    ````

- 进入pod

    ````bash
    kubectl exec -n pytorch-namespace -it pytorch-deployment-db5d59bcb-ptqnp -- /bin/bash
    ````

- 打印PyTorch信息

    ````bash
    python -c "import torch; print(torch.__version__); print(torch.tensor([1.0, 2.0, 3.0]) + torch.tensor([4.0, 5.0, 6.0]))"
    ````

