# How to Use the kubernetes-1.31.1 Plug-in

**The Kubernetes deployment capability of this plug-in is provided by [@Ultraji](https://atomgit.com/ultraji).**

## Example of Quick Deployment of kubernetes-1.31.1

1. Prepare several nodes (Layer 3 network interconnection). The OS version must be openEuler 24.03 or any LTS version of 22.03, and the specifications must be higher than 2U4G.

2. On any node, download and install the oeDeploy command line tool `oedp (version >= 1.1.0-2)`.

    ````bash
    wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.0-2.oe2403sp2.noarch.rpm
    yum install -y oedp-1.1.0-2.oe2403sp2.noarch.rpm
    ````

3. Obtain and initialize the `kubernetes-1.31.1` plug-in.

    ```shell
    oedp repo update
    oedp init kubernetes-1.31.1
    ```

4. Run the `info` command to view the plug-in details.

    ```shell
    oedp info -p kubernetes-1.31.1
    ```

5. Modify the project configuration file and configure the node information based on site requirements.

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
              ansible_password: ""
              architecture: amd64              # e.g. [ amd64, arm64 ]
              oeversion: 24.03-LTS             # e.g. [ 22.03-LTS, 24.03-LTS ]
              runtime: docker                  # e.g. [ docker, containerd ]
        workers:
          hosts:
            192.168.10.2:
              ansible_host: 192.168.10.2
              ansible_port: 22
              ansible_user: root
              ansible_password: ""
              architecture: amd64
              oeversion: 24.03-LTS
              runtime: docker
            192.168.10.3:
              ansible_host: 192.168.10.3
              ansible_port: 22
              ansible_user: root
              ansible_password: ""
              architecture: amd64
              oeversion: 24.03-LTS
              runtime: docker
        new-workers:  # The new-workers field cannot be deleted.
          hosts:
      vars:
        ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
    
        init_cluster_force: "true"            # e.g. [ "true", "false" ] Forcibly initialize the cluster.
        remove_master_no_schedule_taints: "true"
        service_cidr: 10.96.0.0/16            # Service CIDR block
        pod_cidr: 10.244.0.0/16               # Pod IP address segment
        certs_expired: 3650                    # Certificate expiration time
        # lb_kube_apiserver_ip:
        lb_kube_apiserver_port: 8443
        has_deployed_containerd: "false"      # e.g. [ "true", "false" ] Whether containerd has been deployed
        
        # The following parameters must be the same as those in the `host.ini` file during the build process. If they are not involved, ignore them.
        kubernetes_version: 1.31.1
        calico_version: 3.28.2
        pause_image: "registry.k8s.io/pause:3.10"
    
    ````

6. Run the following commands to start automatic deployment.

    ```shell
    oedp run install -p kubernetes-1.31.1
    ```

7. Run the following command to uninstall Kubernetes.

    ```shell
    oedp run uninstall -p kubernetes-1.31.1
    ```

    > -The `p` parameter indicates the directory where the oeDeploy project is located.

## Plugin Creation Guide

1.Environment Setup

Install the dependency software `tar` and `docker` (version > 20.xx) based on the LTS version of openEuler 22.03/24.03.

> Tip: A newer Docker version can be obtained from the upstream community. docker-25.0.3 can be obtained from the repo of openEuler 24.09. Temporarily change the yum source to openEuler 24.09, install the new Docker version, and then restore the yum source.

2.Build Execution

You can adjust the version numbers in the build configuration file `workspace/host.ini` based on your requirements.

Triggering build

```bash
cd oeDeploy/plugins/kubernetes-1.31.1
sudo ./workspace/build
```

> Tip: If the file fails to be downloaded, check the accessibility of network resources based on the error log or configure a proxy in the script.

3.Plug-in Packaging

After the build is complete, the `kubernetes-1.31.1` directory is a complete oeDeploy project. You can use the `oedp` command line tool to start the deployment.

The `tmp` directory is used for resumable file download. After the build is successful, the directory is no longer needed and can be deleted (or backed up to another directory).

```bash
rm -rf workspace/tmp
```

Compress the `kubernetes-1.31.1` directory into a `tar.gz` package to complete the packaging of the oeDeploy plug-in.

```bash
cd ..
tar zcvf kubernetes-1.31.1.tar.gz kubernetes-1.31.1/
```

## Plug-in Maintenance Tips

- Original command: `ansible-playbook -i ../hosts-all.ini -i hosts.ini -e @variables.yml init-k8s.yml`
  In `hosts.ini`, the configuration items involved in the deployment must be included in `config.yaml`.

- The `Ansible` control end (`oedp` software package) depends on `python3-netaddr`.

- Before performing the step `Copy all rpm packages` in `workspace/roles/prepare/base/tasks/main.yml`, install the dependent software package.
  `python3-libselinux`, `python3-netaddr`, `tar`, `socat`, `conntrack-tools`,
  `libnetfilter_cttimeout`, `libnetfilter_cthelper`, `libnetfilter_queue`,
  `ebtables`, and `iptables`

- Due to the `Ansible` version restrictions, you need to replace all `ansible_ssh_host` in the original script with `ansible_host`.

- In the original `workspace/build`, the step of compressing the file into `k8s-install.tar.gz` is not required and can be deleted.
