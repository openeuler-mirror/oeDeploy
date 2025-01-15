# kubeflow自动化部署

基于kubernetes和ansible能力在openEuler服务器上在线部署kubeflow

规格要求

- k8s版本: 1.29+
- 集群规格：仅支持单master集群的kubeflow部署
- 资源规格：32 GB of RAM recommended
           16 CPU cores recommended
- 操作系统版本：22.03-LTS-SPx
- 架构支持：x86_64


```shell
# 修改hosts.ip.ini 配置节点信息
vi hosts.ip.ini

# 测试节点连接，确保所有节点可访问
export ANSIBLE_HOST_KEY_CHECKING=False
ansible all -m ping -i hosts.ip.ini

# 运行kubeflow安装的playbook
ansible-playbook -i hosts.ip.ini init-kubeflow.yml
```