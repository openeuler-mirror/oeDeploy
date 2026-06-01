# Optimal Out-of-the-Box Deployment Guide for Kunpeng BoostKit AccLib Components

## 1. Service Background and Application Scenarios

### 1.1. Service Background

The Kunpeng BoostKit Library provides acceleration libraries optimized based on ARM instructions and developed using the Kunpeng Accelerator Engine (KAE). It covers eight categories of acceleration libraries, involving the system, compression, encryption/decryption, media, math, storage, network, and AI.
They offer high-performance acceleration for various application scenarios such as big data encryption/decryption, SDS compression, and video transcoding.

During the deployment and implementation of the BoostKit libraries, the following pain points are identified:

+ **High learning cost**: There are many types of acceleration library components, and their deployment methods are not unified. The learning curve is steep, and there is a certain threshold for using the components.
+ **Network environment restrictions**: Component deployment depends on network download. In some scenarios, the use of the Internet is restricted, which hinders deployment.
+ **Low deployment efficiency**: When components are deployed on a server cluster, the deployment is time-consuming and labor-intensive due to the large cluster scale, and errors are likely to occur.

The Kunpeng BoostKit automatic deployment plugin developed based on oeDeploy aims to address the preceding pain points. It enables multi-node and multi-component deployment with the simplest user operations. In addition, it meets the requirements of users with restricted Internet access and supports deployment in offline environments, achieving one-click deployment and the optimal out-of-the-box experience.

### 1.2. Typical User Scenarios

| User Type | Requirement Characteristic    | Solution Benefit            |
|-------|----------|------------------|
| Junior developers| Quick test environment setup| Preset optimal configurations and basic deployment completed within 5 minutes|
| Advanced developers| Customized component combinations | On-demand component selection and flexible version specification |
| O&M engineers| Large-scale production deployment | Batch cluster deployment and offline secure deployment |

In addition to the typical users listed above, other users are also welcome to try this plugin. We look forward to your valuable comments.

## 2. Plugin Content

### 2.1. Environment Dependencies

Before using this plugin, ensure that the following conditions are met:

+ There is at least one server that uses the Kunpeng 920 series processor.
+ The OS uses openEuler 22.03-LTS-SP1 or later.
+ The YUM source is available. It can be a network source or a local source.
+ The pip source is available (only for the online deployment solution).
+ The oeDeploy tool has been installed. For details, see [oeDeploy](https://atomgit.com/openeuler/oeDeploy).
+ You have obtained the plugin package and decompressed it. (Obtained from [address](https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/)
Select the online or offline version as required.)
+ In multi-node deployment, nodes can be connected using SSH (password or key).

### 2.2. Directory Structure

The directory structure of the plugin is as follows:

```text
boostkit(boostkit-offline)
|-- config.yaml   # user configuration file
|-- main.yaml     # core function description file of the plugin, which can be ignored by users
|-- doc           # document directory
|   `-- ...
`-- workspace     # working directory, which contains the automatic deployment logic and can be ignored by users
    |-- roles
    |-- ...
```

### 2.3. Function List

This plugin supports the following actions. You can run the `oedp run <action>` command in the CLI to use these actions.

| Supported Action   | Description         |
|------------------|---------------|
| AccLib-show      | Display of the list of acceleration library components that can be deployed|
| AccLib-install   | One-click deployment of the acceleration library components    |
| AccLib-uninstall | One-click uninstallation of the acceleration library components    |

### 2.4. Configuration File

The following is an example of the user configuration file `config.yaml` of this plugin:

```yaml
all:
  hosts:
    host1:
      ansible_host: HOST_IP     # e.g. 192.168.1.101
      ansible_port: 22
      ansible_user: root
      ansible_password: ""
      # Add the proxy based on the actual requirements. When adding the proxy, delete the number signs (#) in the first line and the required line. If the proxy needs to be used globally, move it to all:vars.
      #proxy_env:
      #  http_proxy:
      #  https_proxy:
      #  ftp_proxy:
      #  no_proxy:
    # You can add more hosts here.
  children:
    AccLib:
      hosts:
        host1:
        # You can include more hosts here.
      vars:
        install_list: 'ALL'    # A list or a comma-separated string is supported.
        KSL_version: 2.5.0
        hyperscan_branch: v5.4.2.aarch64
        KAE_branch: kae2
  vars:
    # Skip all basic check items.
    skip_check: false
    # Pip source address. Delete this item if pip installation is not involved.
    pip_index_url: "https://mirrors.huaweicloud.com/repository/pypi/simple"
    # Directory for storing temporary files
    temp_path: /tmp
    # Skip SSH verification. To disable this function, delete the following configuration item.
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
```

You need to configure the IP address, port number, username, and password of the target node (the host where acceleration library components need to be deployed) in `hosts`, and determine whether to use a proxy based on the site requirements. In addition, you can modify the configuration items in
`vars` to change information such as the version of the component to be deployed for customized deployment.

For details about how to configure this file, see the following cases.

## 3. Deployment Process Guide Cases

### 3.1. Junior Developers (Online Deployment)

#### 3.1.1. Instance Background

Student A is a junior developer who has recently started using the Kunpeng ecosystem with limited knowledge of the acceleration library components. Student A wants to quickly get started with Kunpeng development but encounters difficulties when deploying the acceleration library components. In this case, student A needs to use
oeDeploy to quickly deploy the environment and install all available acceleration library components on the local host.

The deployment nodes of student A are as follows.

| # | Node Role     | IP       | Environment Requirement               |
|---|-----------|----------|---------------------|
| 1 | Control node and target node| 10.0.1.1 | YUM, pip, and Internet|

> Explanations:
> 
> + Control node: a node where the oeDeploy tool is installed. You only need to log in to the control node and perform all operations on it.
> + Target node: a node where the acceleration library components are to be installed. Ensure that the target node can communicate with the control node through SSH. You do not need to directly control the target node.
> 
> The control node and target node can be the same machine or different machines. In this case, machine #1 is both the control node and the target node. Therefore, the acceleration library components will be deployed on the current machine.

#### 3.1.2. Deployment Procedure

1. Log in to machine #1.
2. Assume that the plugin package is stored in the `/root/` directory. Go to the plugin package directory:

   ```shell
   cd /root/boostkit && ls
   ```

   Print the files in the directory and ensure that the `config.yaml` and `main.yaml` files and the `workspace` directory exist in the directory.

3. Modify the `config.yaml` file.

   ```shell
   vi config.yaml
   ```

   After the modification, the configuration file is as follows:

   ```yaml
   all:
     hosts:
       host1:
         ansible_host: 10.0.1.1        # IP address of the local host
         ansible_port: 22              # port 22 used for SSH
         ansible_user: root            # Log in as user root if security is ensured.
         ansible_password: ""  # password of user root for logging in to the local host
         # No proxy is used.
     children:
       AccLib:
         hosts:
           host1:   # Only the host name added above needs to be referenced. Ensure that the host name is correct.
         vars:
           install_list: 'ALL'    # If not familiar with the acceleration library components, student A can use 'ALL' to automatically deploy all available components.
           KSL_version: 2.5.0     # Use the default component version.
           hyperscan_branch: v5.4.2.aarch64
           KAE_branch: kae2
     vars:
       # Skip all basic check items.
       skip_check: false
       # Pip source address. Delete this item if pip installation is not involved.
       pip_index_url: "https://mirrors.huaweicloud.com/repository/pypi/simple"
       # Directory for storing temporary files
       temp_path: /tmp
       # Skip SSH verification. To disable this function, delete the following configuration item.
       ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
   ```

   During this process, student A only needs to change the IP address and password.

4. Start automatic deployment.

   ```shell
   oedp run AccLib-install
   ```

   After the execution is complete, the log information on the console displays `Execute succeeded`. At this point, all the acceleration library components that can be installed on the local host are available.

### 3.2. Advanced Developers (Online Deployment)

#### 3.2.1. Instance Background

Ms. B is an experienced Kunpeng developer who has recently developed a piece of software. She now wants to verify the impact of the Kunpeng acceleration library components on the software's running efficiency. To save costs,
Ms. B will temporarily purchase a cloud server to verify the performance and now wants to use the oeDeploy tool to simplify the environment deployment.

The deployment nodes of Ms. B are as follows:

| # | Node Role| IP       | Environment Requirement               |
|---|------|----------|---------------------|
| 1 | Control node| 10.0.2.1 | YUM is available and can communicate with other nodes through SSH. |
| 2 | Target node| 10.0.2.2 | YUM, pip, and Internet|

In this example, node #1 is a local machine used for routine development, and node #2 is a cloud server used for performance verification.

#### 3.2.2. Deployment Procedure

1. Log in to node #1 and go to the plugin directory. (The operations are the same as those in the previous case.)
2. Modify the `config.yaml` file. The result is as follows:

   ```yaml
   all:
     hosts:
       server:      # Change the node name as required.
         ansible_host: 10.0.2.2        # IP address of the cloud server
         ansible_port: 22
         ansible_user: root
         ansible_password: ""  # server password
         # Use a network proxy.
         proxy_env:
           http_proxy: http://user:password@proxy.example.com:8080
           https_proxy: http://user:password@proxy.example.com:8080
           no_proxy: 127.0.0.1,localhost,local
     children:
       AccLib:
         hosts:
           server:  # Change the node name accordingly.
         vars:
           install_list: 'ALL' # Retain the default values for all configurations.
           KSL_version: 2.5.0
           hyperscan_branch: v5.4.2.aarch64
           KAE_branch: kae2
     vars:
       # Skip all basic check items.
       skip_check: false
       # Pip source address. Delete this item if pip installation is not involved.
       pip_index_url: "https://mirrors.huaweicloud.com/repository/pypi/simple"
       # Directory for storing temporary files
       temp_path: /tmp
       # Skip SSH verification. To disable this function, delete the following configuration item.
       ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
   ```

3. Check the available deployment list:

   ```shell
   oedp run AccLib-show
   ```

   This command checks the environment of the target node and prints the list of available acceleration library components, but does not perform any actual installation. This helps you select appropriate components. At the end of the console output, the following debugging information is displayed, indicating the list of acceleration library components that can be installed on the machine:

   ```text
   "msg": [
       "Hyperscan Libgcrypt KAE KQMalloc"
   ]
   ```

4. Based on the result of the previous step, Ms. B decides to use KQMalloc and Hyperscan to optimize performance. In this case, further modify the `config.yaml` file. The result is as follows:

   ```yaml
   all:
     hosts:
       server:      # Change the node name as required.
         ansible_host: 10.0.2.2        # IP address of the cloud server
         ansible_port: 22
         ansible_user: root
         ansible_password: ""  # server password
         # Use a network proxy.
         proxy_env:
           http_proxy: http://user:password@proxy.example.com:8080
           https_proxy: http://user:password@proxy.example.com:8080
           no_proxy: 127.0.0.1,localhost,local
     children:
       AccLib:
         hosts:
           server:  # Change the node name accordingly.
         vars:
           install_list: 'KQMalloc,Hyperscan'    # KQMalloc and Hyperscan need to be installed.
           KSL_version: 2.5.0          # KQMalloc is a part of KSL. You can modify this configuration to change the version.
           hyperscan_branch: v5.4.2.aarch64  # The Hyperscan version can be configured.
           KAE_branch: kae2
     vars:
       # Skip all basic check items.
       skip_check: false
       # Pip source address. Delete this item if pip installation is not involved.
       pip_index_url: "https://mirrors.huaweicloud.com/repository/pypi/simple"
       # Directory for storing temporary files
       temp_path: /tmp
       # Skip SSH verification. To disable this function, delete the following configuration item.
       ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
   ```

   During the entire process, the following configuration items are modified:
    + Node information: node name, node IP address, node password, and network proxy
    + Installation information: list of components to be installed and version information
   > In this example, multiple components need to be deployed at a time. You can enter multiple components in `install_list` and separate the component names with commas (,). You can also use the YAML list syntax. For example:
   > ```yaml
   > install_list:
   >   - 'KQMalloc'
   >   - 'Hyperscan'
   > ```

5. Start automatic deployment.

   ```shell
   oedp run AccLib-install
   ```

   After the execution is complete, the KQMalloc and Hyperscan components are deployed.

### 3.3. Cluster Maintenance Personnel (Offline Deployment)

#### 3.3.1. Instance Background

Mr. C is an O&M engineer of a company and is responsible for maintaining the server cluster. According to service requirements, he needs to deploy the KAE components of the Kunpeng Library on a server cluster. The cluster contains a large number of nodes, and the installation is time-consuming and labor-intensive. Therefore, the oeDeploy tool is required to reduce repeated work. In addition, according to the company's information security regulations, the server cluster cannot be connected to the Internet. Therefore, the offline deployment solution must be used.

The following table lists some nodes in the server cluster. (In practice, there may be more target nodes. Here, only three nodes are listed for demonstration.)

| # | Node Role| IP        | Environment Requirement                    |
|---|------|-----------|--------------------------|
| 1 | Control node| 100.0.1.1 | The YUM and the Internet are available, and the node can communicate with other nodes through SSH.|
| 2 | Target node| 100.0.2.1 | The YUM is available.                  |
| 3 | Target node| 100.0.2.2 | The YUM is available.                  |
| 4 | Target node| 100.0.2.3 | The YUM is available.                  |

Among all nodes, only node #1 requires Internet access. This ensures the network security of the cluster.

> Note: If the cluster needs to be completely disconnected from the Internet, that is, node #1 in this example is not allowed to connect to the Internet, you can use a machine that can access the Internet outside the cluster to replace node #1. After completing the following building and packaging operations, copy the plugin package to node #1 in a non-network mode (for example, using a USB flash drive), and then complete the remaining deployment steps.

#### 3.3.2. Packaging Procedure

1. Log in to node #1 and go to the plugin directory. The method is the same as above. **Note: Use the offline version (boostkit-offline) of this plugin.**
2. Modify the acceleration library to build the configuration file as required.

   ```shell
   vi workspace/build/AccLib/source.cfg
   ```

   The result is as follows:

   ```shell
   KSL_version="2.5.0"
   Hyperscan_git="https://gitee.com/kunpengcompute/hyperscan.git"
   Hyperscan_branch="v5.4.2.aarch64"
   KAE_git="https://gitee.com/kunpengcompute/KAE.git"
   KAE_branch="kae2"
   ```

3. Perform the building:

   ```shell
   sh workspace/build.sh
   ```

   Wait until the download is complete. During this process, ensure that the network connection is normal.

4. (Optional) Determine whether to compress the plugin into a package based on the site requirements.

   ```shell
   cd .. && tar -zcvf boostkit-offline.tar.gz boostkit-offline/
   ```

   In this case, this step is not required.

#### 3.3.3. Deployment Procedure

1. (Optional) Copy the built offline plugin package to the control node, decompress the package, and go to the plugin directory. In this case, this step is not required.
2. Modify the `config.yaml` file. The result is as follows:

   ```yaml
   all:
     hosts:
       100.0.2.1:      # Change the node name to the IP address to facilitate log viewing and debugging.
         ansible_host: 100.0.2.1    # IP address of the target node
         ansible_port: 22
         ansible_user: root
         ansible_password: ""       # No password is required here because the SSH key is configured in the server cluster.
       100.0.2.2:
         ansible_host: 100.0.2.2
         ansible_port: 22
         ansible_user: root
         ansible_password: ""
       100.0.2.3:
         ansible_host: 100.0.2.3
         ansible_port: 22
         ansible_user: root
         ansible_password: ""
     children:
       AccLib:
         hosts:
           100.0.2.1:   # Import the configured node names one by one.
           100.0.2.2:
           100.0.2.3:
         vars:
           install_list: 'KAE' # Only KAE needs to be deployed.
     vars:
       # Skip all basic check items.
       skip_check: false
       # Directory for storing temporary files
       temp_path: /tmp/20250501   # custom temporary file path
       # Skip SSH verification. To disable this function, delete the following configuration item.
       ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
   ```

   **Note: You are advised to use the SSH password for connection only in the debugging environment. In the production environment, you are advised to use the SSH key for connection, which is more secure and does not require a password in the configuration file.**

3. Start automatic deployment.

   ```shell
   oedp run AccLib-install
   ```

   After the deployment starts, all target machines are delivered with tasks and the installation is performed synchronously. After the installation is complete, the acceleration library components are installed on the machines in the cluster.

## 4. Recommendations

+ [oeDeploy command line tool usage guide](https://atomgit.com/openeuler/oeDeploy/blob/master/doc/en/Command.md)
+ [Introduction to the Kunpeng BoostKit Library](https://www.hikunpeng.com/developer/boostkit/library)
