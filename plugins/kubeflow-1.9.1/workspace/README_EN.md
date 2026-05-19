# Kubeflow Automatic Deployment

Online deployment of Kubeflow on openEuler servers based on Kubernetes and Ansible capabilities

Specifications

- Kubernetes version: 1.29+
- Cluster specifications: Only single-master cluster deployment of Kubeflow is supported.
- Resource specifications: 32 GB of RAM recommended
           16 CPU cores recommended
- OS version: 22.03-LTS-SPx
- Architecture: x86_64


```shell
# Modify the hosts.ip.ini configuration node info.
vi hosts.ip.ini

# Test the node connection to ensure that all nodes are accessible.
export ANSIBLE_HOST_KEY_CHECKING=False
ansible all -m ping -i hosts.ip.ini

# Run the playbook for installing Kubeflow.
ansible-playbook -i hosts.ip.ini init-kubeflow.yml
```
