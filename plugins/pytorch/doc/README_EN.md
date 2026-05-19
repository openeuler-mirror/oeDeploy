# PyTorch Deployment Using oeDeploy Based on a Kubernetes Cluster

1. Prepare a Kubernetes cluster.

2. Download the oedp command line tool and install it using yum. If a new oedp version is available, you can use the new version.

   ````bash
   wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.0-3.oe2403sp2.noarch.rpm
   yum install -y oedp-1.1.0-3.oe2403sp2.noarch.rpm
   ````

3. Obtain and initialize the `pytorch` plug-in.

    ```shell
    oedp repo update
    oedp init pytorch
    ```
   
4. Modify `config.yaml` based on site requirements. Ensure that the target node is the master node of Kubernetes. `kubectl_apply` must correspond to the playbook in the workspace.

5. One-click deployment

   ````bash
   oedp run install -p pytorch  # -p < plug-in directory >
   ````

6. One-click uninstallation

   ````bash
   oedp run uninstall -p pytorch  # -p < plug-in directory >
   ````

# demo

## Demo 1: Deploy and print PyTorch information

1. Modify `config.yaml` based on site requirements. The following are examples.

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
          training:
            epoch: 2
      ````

2. Perform one-click deployment.

    ```shell
    oedp run install -p pytorch
    ```

3. View the pod.

    ````bash
    kubectl get pods -n pytorch-namespace
    ````shell
    The command output is as follows.
    ````shell
    NAME                                 READY   STATUS    RESTARTS   AGE
    pytorch-deployment-db5d59bcb-ptqnp   1/1     Running   0          15m
    ````shell

4. View the port mapping.

    ````bash
    kubectl get svc -n pytorch-namespace
    ````shell
   The command output is as follows.
    ````shell
    NAME              TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
    pytorch-service   NodePort   10.96.50.156   <none>        80:30699/TCP   15m
    ````shell

5. Accessing a web page

    ````shell
    http://x.x.x.x:30699/ # node where the master is located
    ````

6. Access the container.

    ````bash
    kubectl exec -n pytorch-namespace -it pytorch-deployment-db5d59bcb-ptqnp -- /bin/bash
    ````

7. Print the PyTorch info.

    ````bash
    python -c "import torch; print(torch.__version__); print(torch.tensor([1.0, 2.0, 3.0]) + torch.tensor([4.0, 5.0, 6.0]))"
    ````

## Demo 2: Training a Lightweight CNN Model Based on the MNIST Dataset

1. PyTorch has been deployed based on demo 1.

2. Perform one-click automatic model training.

    ````bash
    oedp run train -p pytorch  # -p < plug-in directory >
    ````shell
   The command output is as follows.
   
    ````bash
    ......  
    TASK [Display training output] *****************************************************************************************************************************************************************************************************************
    ok: [localhost] => {
      "msg": [
        "Train Epoch: 0 [0/60000]\tLoss: 2.3114",
        "Train Epoch: 0 [6400/60000]\tLoss: 0.3884",
        "Train Epoch: 0 [12800/60000]\tLoss: 0.1483",
        "Train Epoch: 0 [19200/60000]\tLoss: 0.0510",
        "Train Epoch: 0 [25600/60000]\tLoss: 0.1151",
        "Train Epoch: 0 [32000/60000]\tLoss: 0.0191",
        "Train Epoch: 0 [38400/60000]\tLoss: 0.0690",
        "Train Epoch: 0 [44800/60000]\tLoss: 0.1995",
        "Train Epoch: 0 [51200/60000]\tLoss: 0.0417",
        "Train Epoch: 0 [57600/60000]\tLoss: 0.1821",
        "Test Accuracy: 9862/10000 (98.62%)",
        "Train Epoch: 1 [0/60000]\tLoss: 0.0052",
        ......
        "Train Epoch: 1 [57600/60000]\tLoss: 0.0115",
        "Test Accuracy: 9877/10000 (98.77%)"
      ]
    }
    ````
