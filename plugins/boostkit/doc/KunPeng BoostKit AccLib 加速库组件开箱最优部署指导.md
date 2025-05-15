# KunPeng BoostKit AccLib 加速库组件开箱最优部署指导

## 1. 业务背景与使用场景介绍

### 1.1. 业务背景

鲲鹏 BoostKit 加速库提供基于 ARM 指令深度优化和基于鲲鹏 KAE（鲲鹏硬件加速引擎）开发的加速库，覆盖系统库、压缩、加解密、媒体、数学库、存储、网络、AI
库等8类加速库，为大数据加解密、分布式存储压缩、视频转码等应用场景提供高性能加速。

在 BoostKit 加速库的部署和落地过程中，捕捉到了以下痛点：

+ **学习成本高**：加速库组件种类多，部署方式不统一，用户学习曲线陡峭，具有一定的使用门槛；
+ **网络环境制约**：组件部署依赖网络下载，部分场景下要求互联网使用受到限制，部署存在阻力；
+ **部署效率低**：在服务器集群上部署组件时，由于集群规模庞大，部署工作费时费力，容易出错。

基于 oeDeploy 开发的鲲鹏 BoostKit 自动化部署插件旨在解决以上痛点，以最简单的用户操作实现多节点、多组件的部署，同时兼顾互联网受限的用户需求，满足离线环境的部署需要，真正实现一键部署、开箱最优。

### 1.2. 典型用户场景

| 用户类型  | 需求特征     | 方案价值             |
|-------|----------|------------------|
| 初级开发者 | 快速搭建测试环境 | 预置最优配置，5分钟完成基础部署 |
| 进阶开发者 | 定制化组件组合  | 支持组件按需选用，版本灵活指定  |
| 运维工程师 | 大规模生产部署  | 支持集群批量部署、离线安全部署  |

除了以上列举的典型用户外，也欢迎其他用户体验本插件。期待您的宝贵意见！

## 2. 插件内容介绍

### 2.1. 环境依赖

使用本插件前，您需要确认以下条件是否满足：

+ 至少一台使用 KunPeng 920 系列处理器的服务器；
+ 使用 openEuler 操作系统，且版本不低于 22.03-LTS-SP1；
+ yum 源可用，可以是网络源，也可以是本地源；
+ pip 源可用（仅针对在线部署方案）；
+ 已经安装了 oeDeploy 工具（详见[此处](https://gitee.com/openeuler/oeDeploy)）；
+ 已经获取了本插件的插件包并解压（获取[地址](https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/)
，根据实际需要选择在线或离线版本）
+ 多节点部署时，各个节点之间可用 ssh 连通（密码或密钥）。

### 2.2. 目录结构

插件中的目录结构如下所示：

```text
boostkit(boostkit-offline)
|-- config.yaml   # 用户配置文件
|-- main.yaml     # 插件核心功能描述文件，用户无需关注
|-- doc           # 文档目录
|   `-- ...
`-- workspace     # 工作目录，内含自动化部署逻辑，用户无需关注
    |-- roles
    |-- ...
```

### 2.3. 功能列表

本插件支持以下功能(action)，您可以在命令行执行`oedp run <action>`命令，来使用这些功能：

| 支持功能 (action)    | 功能详情          |
|------------------|---------------|
| AccLib-show      | 显示可部署的加速库组件列表 |
| AccLib-install   | 一键部署加速库组件     |
| AccLib-uninstall | 一键卸载加速库组件     |

### 2.4. 配置文件

本插件的用户配置文件`config.yaml`示例如下：

```yaml
all:
  hosts:
    host1:
      ansible_host: HOST_IP     # e.g. 192.168.1.101
      ansible_port: 22
      ansible_user: root
      ansible_password: ""
      # 按实际代理需要添加，添加时删除以下第一行和所需行的井号；如需全局使用代理请移动至 all:vars
      #proxy_env:
      #  http_proxy:
      #  https_proxy:
      #  ftp_proxy:
      #  no_proxy:
    # 可在此添加更多主机
  children:
    AccLib:
      hosts:
        host1:
        # 可在此包含更多主机
      vars:
        install_list: 'ALL'    # 支持使用列表，或者使用逗号分隔的字符串
        KSL_version: 2.5.0
        hyperscan_branch: v5.4.2.aarch64
        KAE_branch: kae2
  vars:
    # 跳过所有基本检查项
    skip_check: false
    # pip 源地址，如不涉及 pip 安装可删除此项
    pip_index_url: "https://mirrors.huaweicloud.com/repository/pypi/simple"
    # 临时文件存放目录
    temp_path: /tmp
    # 跳过 ssh 校验，如需禁用此功能，请删除以下配置项
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
```

用户需要在`hosts`部分配置目标节点（需要部署加速库组件的机器）的 IP、端口、用户、密码等信息，并根据实际需要决定是否使用代理。此外，还可以修改
`vars`中的配置项，更改部署的组件的版本等信息，实现自定义部署。

关于此配置文件的具体配置方法，建议参考下文中的案例来配置。

## 3. 部署流程指导实例

### 3.1. 初级开发者（在线部署）

#### 3.1.1. 实例背景

A 同学是一名接触鲲鹏开发时间不久的初级开发者，对加速库组件了解较少，希望快速上手学习鲲鹏开发，此时在部署加速库组件时遇到困难，需要使用
oeDeploy 来快速完成环境部署，将本机器上所有可用的加速库组件都安装上去。

A 同学的部署节点如下：

| # | 节点角色      | IP       | 环境要求                |
|---|-----------|----------|---------------------|
| 1 | 控制节点、目标节点 | 10.0.1.1 | yum 可用、pip 可用、互联网可用 |

    解释：
    控制节点：安装有 oeDeploy 工具的节点，用户仅需要登录控制节点，并在此完成所有操作；
    目标节点：待安装加速库组件的节点，需要确保与控制节点之间 ssh 连通，用户不需要直接控制目标节点。
    控制节点与目标节点可以是同一台机器，也可以不是同一台机器。在此案例中，#1 号机器既是控制节点，也是目标节点，那么加速库组件将会被部署在当前机器上。

#### 3.1.2. 部署步骤

1. 登录 #1 号机器；
2. 假设插件包位于`/root/`目录下。进入插件包目录：
   ```shell
   cd /root/boostkit && ls
   ```
   打印目录中的文件，确认目录下存在`config.yaml`、`main.yaml`文件以及`workspace`目录；
3. 修改`config.yaml`文件：
   ```shell
   vi config.yaml
   ```
   将配置文件修改后如下所示：
   ```yaml
   all:
     hosts:
       host1:
         ansible_host: 10.0.1.1        # 本机 IP
         ansible_port: 22              # ssh 使用 22 端口
         ansible_user: root            # 安全性允许的情况下，使用 root 用户登录
         ansible_password: "12345678"  # 本机 root 密码
         # 不使用代理
     children:
       AccLib:
         hosts:
           host1:   # 此处仅需要引用上面添加的主机名，确保主机名相对应即可
         vars:
           install_list: 'ALL'    # A 同学不熟悉加速库组件，使用 'ALL' 可自动部署所有可用的组件
           KSL_version: 2.5.0     # 组件版本信息一律使用默认值
           hyperscan_branch: v5.4.2.aarch64
           KAE_branch: kae2
     vars:
       # 跳过所有基本检查项
       skip_check: false
       # pip 源地址，如不涉及 pip 安装可删除此项
       pip_index_url: "https://mirrors.huaweicloud.com/repository/pypi/simple"
       # 临时文件存放目录
       temp_path: /tmp
       # 跳过 ssh 校验，如需禁用此功能，请删除以下配置项
       ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
   ```
   在此过程中，A 同学仅需修改 IP 和密码即可完成配置。
4. 开始自动部署：
   ```shell
   oedp run AccLib-install
   ```
   等待运行完成后，本机上所有可安装的加速库组件就已经全部可用了。

### 3.2. 进阶开发者（在线部署）

#### 3.2.1. 实例背景

B 女士是一名有经验的鲲鹏开发者，最近开发了一款软件，现在想要验证鲲鹏加速库组件对其运行效率的影响。为了节约成本，B
女士将临时购买一台云服务器来验证性能，现在希望使用 oeDeploy 工具来简化环境部署工作。

B 女士的部署节点如下：

| # | 节点角色 | IP       | 环境要求                |
|---|------|----------|---------------------|
| 1 | 控制节点 | 10.0.2.1 | yum 可用、与其他节点 ssh 通  |
| 2 | 目标节点 | 10.0.2.2 | yum 可用、pip 可用、互联网可用 |

在此案例中，#1 号节点是本地机器，主要用于日常开发，#2 号节点是云服务器，用于验证性能。

#### 3.2.2. 部署步骤

1. 登录 #1 号机器并进入插件目录（操作同上一案例，此处省略）
2. 修改`config.yaml`文件，结果如下：
   ```yaml
   all:
     hosts:
       server:      # 可自由修改节点名称
         ansible_host: 10.0.2.2        # 云服务器 IP
         ansible_port: 22
         ansible_user: root
         ansible_password: "12345678"  # 服务器密码
         # 使用网络代理
         proxy_env:
           http_proxy: http://user:password@proxy.example.com:8080
           https_proxy: http://user:password@proxy.example.com:8080
           no_proxy: 127.0.0.1,localhost,local
     children:
       AccLib:
         hosts:
           server:  # 对应修改节点名称
         vars:
           install_list: 'ALL'    # 所有配置暂时保持默认值
           KSL_version: 2.5.0
           hyperscan_branch: v5.4.2.aarch64
           KAE_branch: kae2
     vars:
       # 跳过所有基本检查项
       skip_check: false
       # pip 源地址，如不涉及 pip 安装可删除此项
       pip_index_url: "https://mirrors.huaweicloud.com/repository/pypi/simple"
       # 临时文件存放目录
       temp_path: /tmp
       # 跳过 ssh 校验，如需禁用此功能，请删除以下配置项
       ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
   ```
3. 检查可用部署列表：
   ```shell
   oedp run AccLib-show
   ```
   此命令将会检查目标节点的环境，并打印可用的加速库组件列表，而不会执行任何实际安装的工作，方便用户选用合适的组件。在控制台输出的最后，会打印如下所示的调试信息，表示这台机器可以安装的加速库组件列表：
   ```text
   "msg": "Hyperscan KAE KQMalloc Libgcrypt"
   ```
4. 根据上一步的结果，B 女士决定仅尝试使用内存加速库 KQMalloc 来优化性能，此时进一步修改`config.yaml`，结果如下：
   ```yaml
   all:
     hosts:
       server:      # 可自由修改节点名称
         ansible_host: 10.0.2.2        # 云服务器 IP
         ansible_port: 22
         ansible_user: root
         ansible_password: "12345678"  # 服务器密码
         # 使用网络代理
         proxy_env:
           http_proxy: http://user:password@proxy.example.com:8080
           https_proxy: http://user:password@proxy.example.com:8080
           no_proxy: 127.0.0.1,localhost,local
     children:
       AccLib:
         hosts:
           server:  # 对应修改节点名称
         vars:
           install_list: 'KQMalloc'    # 只需要安装 KQMalloc
           KSL_version: 2.4.0          # KQMalloc 是 KSL 的一部分，可配置此处版本信息
           hyperscan_branch: v5.4.2.aarch64   # 其他版本信息不变
           KAE_branch: kae2
     vars:
       # 跳过所有基本检查项
       skip_check: false
       # pip 源地址，如不涉及 pip 安装可删除此项
       pip_index_url: "https://mirrors.huaweicloud.com/repository/pypi/simple"
       # 临时文件存放目录
       temp_path: /tmp
       # 跳过 ssh 校验，如需禁用此功能，请删除以下配置项
       ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
   ```
   在整个过程中，经过修改的配置项有：
    + 节点信息：节点名称、节点 IP、节点密码、网络代理；
    + 安装信息：安装组件列表、版本信息
5. 开始自动部署：
   ```shell
   oedp run AccLib-install
   ```
   等待运行完成后，内存加速库组件 KQMalloc 就部署完成了。

### 3.3. 集群维护人员（离线部署）

#### 3.3.1. 实例背景

C 先生是一家公司的运维工程师，负责服务器集群维护工作，根据业务需要，将在一个服务器集群上部署鲲鹏加速库 KAE 和 Hyperscan
组件。由于集群中节点数量庞大，安装工作费时费力，需要使用 oeDeploy 工具减少重复劳动。另外，根据公司信息安全规定，服务器集群不允许接入互联网，因此必须采用离线部署方案。

服务器集群的部分节点如下（实际情况下目标节点数量可能更多，此处仅列举三台作为展示）：

| # | 节点角色 | IP        | 环境要求                     |
|---|------|-----------|--------------------------|
| 1 | 控制节点 | 100.0.1.1 | yum 可用、互联网可用、与其他节点 ssh 通 |
| 2 | 目标节点 | 100.0.2.1 | yum 可用                   |
| 3 | 目标节点 | 100.0.2.2 | yum 可用                   |
| 4 | 目标节点 | 100.0.2.3 | yum 可用                   |

所有节点中，仅 #1 号节点需要具备互联网，而其他节点均不需要互联网接入，可以确保集群的网络安全。

    如果要求集群完全脱网，即不允许本例中的 #1 号机器连接互联网，可以通过集群之外的能够使用互联网的机器代替 #1 号机器，完成下面的构建打包操作后，通过非网络方式（例如使用U盘）将插件包拷贝至 #1 号节点，然后完成剩余的部署步骤。

#### 3.3.2. 打包步骤

1. 登录 #1 号节点，并进入插件目录，方法同上；（**注意：此处需使用本插件的离线版本 boostkit-offline**）
2. 根据实际需要修改加速库构建配置文件：
   ```shell
   vi workspace/build/AccLib/source.cfg
   ```
   结果如下：
   ```shell
   KSL_version="2.5.0"
   Hyperscan_git="https://gitee.com/kunpengcompute/hyperscan.git"
   Hyperscan_branch="v5.4.2.aarch64"
   KAE_git="https://gitee.com/kunpengcompute/KAE.git"
   KAE_branch="kae2"
   ```
3. 执行构建：
   ```shell
   sh workspace/build.sh
   ```
   耐心等待下载完成，在此过程中请确保网络畅通。
4. （可选）根据实际需要决定是否将插件打成压缩包：
   ```shell
   cd .. && tar -zcvf boostkit-offline.tar.gz boostkit-offline/
   ```
   在本案例中，无需进行这一步骤。

#### 3.3.3. 部署步骤

1. （可选）将构建好的离线插件包拷贝至控制节点，解压后进入插件目录。在本案例中，无需进行这一步骤。
2. 修改`config.yaml`文件，结果如下：
   ```yaml
   all:
     hosts:
       100.0.2.1:      # 把节点名称改为 IP，方便查看日志及调试
         ansible_host: 100.0.2.1    # 目标节点 IP
         ansible_port: 22
         ansible_user: root
         ansible_password: ""       # 服务器集群中配置了 ssh 密钥，此处无需填写密码
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
           100.0.2.1:   # 只需要将上面配置的节点名称依次在此处引入即可
           100.0.2.2:
           100.0.2.3:
         vars:
           install_list: 'KAE,Hyperscan'  # 可一次性部署多种组件
     vars:
       # 跳过所有基本检查项
       skip_check: false
       # 临时文件存放目录
       temp_path: /tmp/20250501   # 自定义的临时文件路径
       # 跳过 ssh 校验，如需禁用此功能，请删除以下配置项
       ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
   ```
   **提示：建议仅在调试环境使用 ssh 密码连接，而在生产环境推荐使用 ssh 密钥连接。使用密钥连接的安全性更高，并且不需要在配置文件中设置密码。**
3. 开始自动部署：
   ```shell
   oedp run AccLib-install
   ```
   开始部署后，所有目标机器会被同步下发任务，并同步执行安装操作，等待执行完成后，集群中的机器就完成了加速库组件的安装。

## 4. 推荐阅读

+ [oeDeploy 命令行工具使用指南](https://gitee.com/openeuler/oeDeploy/blob/master/doc/Command.md)
+ [鲲鹏 BoostKit 加速库介绍](https://www.hikunpeng.com/developer/boostkit/library)