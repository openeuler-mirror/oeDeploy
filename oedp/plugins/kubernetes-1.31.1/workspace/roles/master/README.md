# kubeadm

1. 如何生成kubeadm配置文件

```shell
kubeadm config print init-defaults > kubeadm-init.yaml
kubeadm config print join-defaults > kubeadm-join.yaml
```