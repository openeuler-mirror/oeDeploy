# kubernetes-1.31.1 插件使用说明

**本插件的 kubernetes 部署能力由 [@Ultraji](https://gitee.com/ultraji)  提供**

## kubernetes-1.31.1 一键部署操作示例

1. 准备若干节点（三层网络互通），OS 版本为 openEuler 24.03 或 22.03 的任意 LTS 版本，规格大于 2U4G。

2. 在任意节点上，下载并安装 oeDeploy 的命令行工具`oedp (version >= 1.1.0-2)`。
    ````bash
    wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.0-2.oe2403sp2.noarch.rpm
    yum install -y oedp-1.1.0-3.oe2403sp2.noarch.rpm
    ````

3. 获取并初始化`kubernetes-1.31.1`插件。
    ```shell
    oedp repo update
    oedp init kubernetes-1.31.1
    ```

4. 执行`info`命令以查看插件详细信息：
    ```shell
    oedp info -p kubernetes-1.31.1
    ```

5. 修改项目配置文件，根据实际情况配置节点信息：
    ```shell
    vim kubernetes-1.31.1/config.yaml
    ```

    ````yaml
    all:
      children:
        masters:
          hosts:
            192.168.10.1:
              ansible_host: 192.168.10.1
              ansible_port: 22
              ansible_user: root
              ansible_password: "xxxxxxxx"
              architecture: amd64              # e.g. [ amd64, arm64 ]
              oeversion: 24.03-LTS             # e.g. [ 22.03-LTS, 24.03-LTS ]
              runtime: docker                  # e.g. [ docker, containerd ]
        workers:
          hosts:
            192.168.10.2:
              ansible_host: 192.168.10.2
              ansible_port: 22
              ansible_user: root
              ansible_password: "xxxxxxxx"
              architecture: amd64
              oeversion: 24.03-LTS
              runtime: docker
            192.168.10.3:
              ansible_host: 192.168.10.3
              ansible_port: 22
              ansible_user: root
              ansible_password: "xxxxxxxx"
              architecture: amd64
              oeversion: 24.03-LTS
              runtime: docker
        new-workers:  # new-workers字段不可删除
          hosts:
      vars:
        ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
    
        init_cluster_force: "true"             # e.g. [ "true", "false" ]  强制初始化集群
        remove_master_no_schedule_taints: "true"
        service_cidr: 10.96.0.0/16             # 服务网段
        pod_cidr: 10.244.0.0/16                # pod ip 网段
        certs_expired: 3650                    # 证书过期时间
        # lb_kube_apiserver_ip:
        lb_kube_apiserver_port: 8443
        has_deployed_containerd: "false"       # e.g. [ "true", "false" ]  是否已有 containerd
        
        # 以下参数需要与build过程中的host.ini保持一致，如果不涉及请忽视
        kubernetes_version: 1.31.1
        calico_version: 3.28.2
        pause_image: "registry.k8s.io/pause:3.10"
    
    ````

6. 执行以下命令以开始自动化部署：
    ```shell
    oedp run install -p kubernetes-1.31.1
    ```

7. 执行以下命令以卸载kubernetes：
    ```shell
    oedp run uninstall -p kubernetes-1.31.1
    ```

    > -p 参数表示 oeDeploy 项目所在目录

## 插件构建指导

1. 环境准备

基于 openEuler22.03 / 24.03 的 LTS 版本，安装依赖软件`tar`、`docker`(version > 20.xx)

> Tip: 较新的 docker 版本可以从上游社区获取。docker-25.0.3 可以从 openEuler24.09 的 repo 中获取，临时修改 yum 源到 openEuler24.09，安装新版本 docker 后恢复。

2. 构建执行

可以根据实际需求，在构建配置文件`workspace/host.ini`中调整相关版本号。

触发构建：

```bash
cd oeDeploy/plugins/kubernetes-1.31.1
sudo ./workspace/build
```

> Tip: 如果遇到文件下载失败，请根据错误日志，检查网络资源的可访问状态，或在脚本中配置代理。

3. 插件打包

构建完成后的`kubernetes-1.31.1`目录，已经是一个完整的 oeDeploy 项目，可以用`oedp`命令行工具开始部署。

`tmp`目录用于文件下载的断点续传，构建成功后就不再需要，可以删除（或者备份到其他目录）。

```bash
rm -rf workspace/tmp
```

将`kubernetes-1.31.1`目录打包成`tar.gz`格式，完成 oeDeploy 插件的打包。

```bash
cd ..
tar zcvf kubernetes-1.31.1.tar.gz kubernetes-1.31.1/
```

## 插件维护Tips

- 原始命令行`ansible-playbook -i ../hosts-all.ini -i hosts.ini -e @variables.yml init-k8s.yml`
  `hosts.ini`中，在部署过程中所涉及的配置项，需要体现在`config.yaml`

- `ansible`控制端(`oedp`软件包)依赖`python3-netaddr`

- `workspace/roles/prepare/base/tasks/main.yml`的步骤`Copy all rpm packages`前需要安装依赖软件包：
  `python3-libselinux`、`python3-netaddr`、`tar`、`socat`、`conntrack-tools`、
  `libnetfilter_cttimeout`、`libnetfilter_cthelper`、`libnetfilter_queue`、
  `ebtables`、`iptables`

- 受`ansible`版本限制，需将原始脚本中所有`ansible_ssh_host`替换成`ansible_host`

- 原始`workspace/build`中，最后压缩为`k8s-install.tar.gz`的步骤不需要，可以删除
