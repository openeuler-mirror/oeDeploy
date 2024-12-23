## 基于KServe部署一个推理服务

### 第一步：部署**InferenceService推理服务**

执行命令，创建一个名为**sklearn-iris**的InferenceService推理服务。

该推理服务将使用iris （鸢尾花）数据集训练的scikit-learn模型。

该数据集具有三个输出类别：

- Iris Setosa（山鸢尾，索引：0）
- Iris Versicolour（杂色鸢尾花，索引：1）
- Iris Virginica（弗吉尼亚鸢尾，索引：2）

```
kubectl apply -f - <<EOF
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "sklearn-iris"
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "gs://kfserving-examples/models/sklearn/1.0/model"
EOF
```

执行命令，检查服务状态

```
kubectl get inferenceservices sklearn-iris
```

预期输出

```
NAME           URL                                             READY   PREV   LATEST   PREVROLLEDOUTREVISION   LATESTREADYREVISION            AGE
sklearn-iris   http://sklearn-iris.default.svc.cluster.local   True           100                              sklearn-iris-predictor-00001   26h
```

### 第二步：访问服务

执行如下命令，访问服务

```
curl -v "http://sklearn-iris.default.svc.cluster.local/v1/models/sklearn-iris:predict" -d '{"instances": [[6.8,  2.8,  4.8,  1.4], [6.0,  3.4,  4.5,  1.6]]}' -H "Content-Type: application/json"
```

预期结果

```
-Type: application/json"
*   Trying 10.96.79.71:80...
* Connected to sklearn-iris.default.svc.cluster.local (10.96.79.71) port 80 (#0)
> POST /v1/models/sklearn-iris:predict HTTP/1.1
> Host: sklearn-iris.default.svc.cluster.local
> User-Agent: curl/7.79.1
> Accept: */*
> Content-Type: application/json
> Content-Length: 65
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< content-length: 21
< content-type: application/json
< date: Thu, 12 Dec 2024 12:46:41 GMT
< server: istio-envoy
< x-envoy-upstream-service-time: 4
<
* Connection #0 to host sklearn-iris.default.svc.cluster.local left intact
{"predictions":[1,1]}
```

结果返回了两个预测` {"predictions": [1, 1]}`，该结果为推理发送的两组数据点对应于索引为1的花，模型预测这两种花都是Iris Versicolour（杂色鸢尾花）。 