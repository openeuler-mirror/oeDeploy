# 1. 安装katib
a) 使用以下命令安装kubeflow
```
oedp run install -p ~/kubeflow-1.9.1/
```
b) 使用如下命令安装katib
```
oedp run install-katib -p kubeflow-1.9.1/
```
c) 测试katib是否安装成功，katib相关的pod状态正常
```
[root@master2 ~]# kubectl get pod -n kubeflow | grep katib
katib-controller-855cf4d89c-sg2gp                    1/1     Running   0              13h
katib-db-manager-8d6fbf94b-8kqs9                     1/1     Running   3 (13h ago)    13h
katib-mysql-6fffd89b48-sh59s                         1/1     Running   1 (13h ago)    13h
katib-ui-76745d6dd6-qnn84                            2/2     Running   0              13h
[root@master2 ~]#
```
d) 转发kubeflow接口
```
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80 --address 192.168.122.133
```
# 2. 测试katib用例
a) 浏览器上输入http://192.168.122.133:8080，登录kubeflow，默认用户名/密码为user@example.com/12341234

b) 进入Katib Experiments，点击页面右侧New Experiment，点击Edit，输入以下内容，点击CREATE，稍等一段时间后，可在网页上查看执行结果
```
apiVersion: kubeflow.org/v1beta1
kind: Experiment
metadata:
  namespace: kubeflow-user-example-com
  name: grid
spec:
  objective:
    type: minimize
    goal: 0.001
    objectiveMetricName: loss
  algorithm:
    algorithmName: grid
  parallelTrialCount: 3
  maxTrialCount: 12
  maxFailedTrialCount: 3
  parameters:
    - name: lr
      parameterType: double
      feasibleSpace:
        min: "0.01"
        step: "0.005"
        max: "0.05"
    - name: momentum
      parameterType: double
      feasibleSpace:
        min: "0.5"
        step: "0.1"
        max: "0.9"
  trialTemplate:
    primaryContainerName: training-container
    trialParameters:
      - name: learningRate
        description: Learning rate for the training model
        reference: lr
      - name: momentum
        description: Momentum for the training model
        reference: momentum
    trialSpec:
      apiVersion: batch/v1
      kind: Job
      spec:
        template:
          spec:
            containers:
              - name: training-container
                image: swr.cn-north-4.myhuaweicloud.com/openeuler-hangzhou/docker.io/kubeflowkatib/pytorch-mnist-cpu:v0.17.0
                command:
                  - "python3"
                  - "/opt/pytorch-mnist/mnist.py"
                  - "--epochs=1"
                  - "--batch-size=16"
                  - "--lr=${trialParameters.learningRate}"
                  - "--momentum=${trialParameters.momentum}"
            restartPolicy: Never
```
