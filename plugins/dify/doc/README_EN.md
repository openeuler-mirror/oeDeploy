# How to Use the Dify Plug-in

## 1. Preparing the Environment

Prepare two nodes (Layer 3 network interconnection). The OS version must be openEuler 24.03 or any LTS version of 22.03, and the specifications must be higher than 2U4G.

## 2. Installing the OEDP

On the controller node, download and install the oeDeploy command line tool `oedp (version >= 1.1.0-2)`.

````bash
wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.0-2.oe2403sp2.noarch.rpm
yum install -y oedp-1.1.0-3.oe2403sp2.noarch.rpm
````

## 3. Obtaining and Learn About the Plug-in

Download the plug-in package `dify.tar.gz` on the controller node and decompress it. The directory structure of plug-in is as follows:

```shell
dify
├── config.yaml
├── doc
│   └── readme.md
├── main.yaml
└── workspace
    ├── check-env.yaml
    ├── files
    │   └── openEuler2409.repo
    ├── install-dify.yaml
    ├── install-docker.yaml
    ├── templates
    │   └── daemon.j2
    └── uninstall-dify.yaml
```

We need to check the `dify/config.yaml` file. Before running the plug-in, ensure that the values of `NODE_NAME`, `NODE_IP`, `NODE_PORT`, `NODE_USER`, and `NODE_PASSWORD` are correctly modified. The details are as follows.

```yaml
all:
  hosts:
    # To be modified. `NODE_NAME` is the unique identifier of the node. Example value: `dify_node`.
    NODE_NAME:
      # To be modified. `NODE_IP` is the IP address of the node. Example value: `192.168.10.1`.
      ansible_host: NODE_IP
      # To be modified. `NODE_PORT` is the port number of the node. Example value: `22`.
      ansible_port: NODE_PORT
      # To be modified. NODE_USER is the username of the node. Example value: root
      ansible_user: NODE_USER
      # To be modified. `NODE_PASSWORD` is the password of the node.
      ansible_password: NODE_PASSWORD
  vars:
    # Minimum configuration requirements for the target node
    # Minimum number of CPU cores
    MIN_CPU: 2
    # Minimum memory
    MIN_MEM_GB: 4

    # Docker image acceleration site
    DOCKER_IMAGE_URL: https://docker.m.daocloud.io

    # Dify source code directory
    DIFY_CODE_DIR: /opt/dify
    # Dify GitHub address
    DIFY_GIT_URL: https://github.com/langgenius/dify.git
    # GitHub proxy
    GITHUB_PROXY: https://gh.idayer.com/

    # Skip SSH verification. (To disable this function, comment out the following configuration item.)
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
```

> **Notice** 
> 
> - If the SSH key pair is used for authentication and the public key of the control node has been added to the `~/.ssh/authorized_keys` file of the target node, leave `NODE_PASSWORD` empty.
> - If `GITHUB_PROXY` is used, the git clone code may fail. In this case, set it to an empty value and try again.

The following two files are described:

- The `dify/workspace/files/openEuler24.09.repo` file provides the Docker installation source, which is stored in the `/etc/yum.repo.d` directory on the target node.

- The `dify/workspace/templates/daemon.j2` file is the Docker configuration file, which is stored in the `/etc/docker` directory on the target node and renamed `daemon.json`.

## 4. Executing the Plug-in

### 4.1 Viewing Plug-in Information

```bash
oedp info -p ./dify
```

> The `-p` option is followed by the directory path of the decompressed plug-in.

Output:

```shell
[ INFO ] - [info_cmd] - name: dify
version: 
description: install and uninstall Dify
action:
+---+-----------+----------------+
| # |   Action  |  Description   |
+---+-----------+----------------+
| 1 |  install  |  Install Dify  |
| 2 | uninstall | Uninstall Dify |
+---+-----------+----------------+
```

> The output indicates that the Dify plug-in has two operations: installing and uninstalling Dify.

### 4.2 Installing Dify

```bash
oedp run install -p ./dify
```

### 4.3 Uninstalling Dify

```bash
oedp run uninstall -p ./dify
```
