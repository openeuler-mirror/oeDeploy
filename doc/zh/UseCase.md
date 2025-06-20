# oeDeploy 应用案例

## 应用案例 1：Kubernetes 一键部署

1. 准备 3 个 2U4G 的虚拟机环境（三层网络互通），使用的 OS 版本为 openEuler 24.03 或 22.03 的任意版本，目标是部署由 1 个 master、2 个 worker 构成的 k8s 集群。

2. 在任意节点上，下载并安装 oeDeploy 的命令行工具 oedp。

    ````bash
    wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.1-0.oe2403sp2.noarch.rpm
    yum install -y oedp-1.1.1-0.oe2403sp2.noarch.rpm
    ````

3. 执行以下命令，获取插件包，确保当前目录下出现了目录`kubernetes-1.31.1`。

    ```shell
    oedp repo update
    oedp init kubernetes-1.31.1
    ```

4. 执行`info`命令以查看插件详细信息。

    ```shell
    oedp info -p kubernetes-1.31.1
    ```

5. 修改项目配置文件，根据实际情况配置节点信息。

    ```shell
    vim kubernetes-1.31.1/config.yaml
    ```

    ````yaml
    all:
      children:
        masters:
          hosts:
            # master节点数量须为奇数
            172.27.76.114:                     # master node IP
              ansible_host: 172.27.76.114      # master node IP
              ansible_port: 22
              ansible_user: root
              ansible_password: ""
              architecture: amd64              # [ amd64, arm64 ]
              oeversion: 24.03-LTS             # [ 22.03-LTS, 24.03-LTS ]
              runtime: docker                  # [ docker, containerd ]
        workers:
          hosts:
            172.27.70.60:                      # worker node IP
              ansible_host: 172.27.70.60       # worker node IP
              ansible_port: 22
              ansible_user: root
              ansible_password: ""
              architecture: amd64
              oeversion: 24.03-LTS
              runtime: docker
            172.27.72.90:
              ansible_host: 172.27.72.90
              ansible_port: 22
              ansible_user: root
              ansible_password: ""
              architecture: amd64
              oeversion: 24.03-LTS
              runtime: docker
        new-workers:  # new-workers 字段不可删除
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

        # 以下参数需要与 build 过程中的 host.ini 保持一致，如果不涉及请忽视
        kubernetes_version: 1.31.1
        calico_version: 3.28.2
        pause_image: "registry.k8s.io/pause:3.10"
    ````

   > 注意：须确保节点间 ssh 可联通，支持密码登录和密钥登录，如果使用密钥登录，则不需要配置密码。

6. 执行以下命令以开始自动化部署。

    ```shell
    oedp run install -p kubernetes-1.31.1
    ```

7. 执行以下命令以卸载 Kubernetes。

    ```shell
    oedp run uninstall -p kubernetes-1.31.1
    ```

   > -p 参数表示解压后的文件目录。如果进入 kubernetes-1.31.1 插件根目录，执行 oedp 命令时无需 -p 参数。

## 应用案例 2：AnythingLLM 一键部署

1. 下载 oedp 命令行工具，并用 yum 安装。如有更新的 oedp 版本，可以选择新版本。

    ```bash
    wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.1-0.oe2403sp2.noarch.rpm
    yum install -y oedp-1.1.1-0.oe2403sp2.noarch.rpm
    ```

2. 获取并初始化`AnythingLLM`插件。

    ```shell
    oedp repo update
    oedp init anythingLLM
    ```

3. 根据实际情况，修改 config.yaml。确保部署节点网络正常。

4. 一键部署：

    ````bash
    oedp run install -p angthingLLM  # -p <插件目录>
    ````

5. 一键卸载：

    ````bash
    oedp run uninstall -p angthingLLM  # -p <插件目录>
    ````

### Demo：部署并打印 AnythingLLM 信息

1. 编辑 config.yaml 文件。

    ````yaml
    all:
    hosts:
      host1:
        ansible_host: 192.168.124.17   # 远端IP
        ansible_port: 22               # 端口号
        ansible_user: root             # 用户名
        ansible_password: passwd       # 密码

    vars:
      docker_download_url:
        x86_64: https://download.docker.com/linux/static/stable/x86_64/docker-26.1.4.tgz
        aarch64: https://download.docker.com/linux/static/stable/aarch64/docker-26.1.4.tgz
      docker_download_path: /tmp
      docker_image_urls: https://docker.m.daocloud.io

      container_name: "anythinglLLM-container"
      docker_image: "mintplexlabs/anythingllm"
      storage_location: "{{ lookup('env', 'HOME') }}/anythingllm"
      host_port: 3001
    ````

2. 进入容器并测试 AnythingLLM 服务。

    - 进入容器：

     ````bash
     docker exec -it anythinglLLM-container /bin/bash
     ````

    - 测试 AnythingLLM 服务：

     ````bash
     curl localhost:3001
     ````

3. 部署环境测试 AnythingLLM 服务。

    ```bash
    -curl 192.168.124.17:3001/ curl localhost:3001
    ```

4. 正常返回如下:

    ```html
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link type="image/svg+xml" href="/favicon.png" >
        <title >AnythingLLM | Your personal LLM trained on anything</title>
        <meta name="title" content="AnythingLLM | Your personal LLM trained on anything" >
        <meta description="title" content="AnythingLLM | Your personal LLM trained on anything" >
        <meta property="og:type" content="website" >
        <meta property="og:url" content="https://anythingllm.com" >
        <meta property="og:title" content="AnythingLLM | Your personal LLM trained on anything" >
        <meta property="og:description" content="AnythingLLM | Your personal LLM trained on anything" >
        <meta property="og:image" content="https://raw.githubusercontent.com/Mintplex-Labs/anything-llm/master/images/promo.png" >
        <meta property="twitter:card" content="summary_large_image" >
        <meta property="twitter:url" content="https://anythingllm.com" >
        <meta property="twitter:title" content="AnythingLLM | Your personal LLM trained on anything" >
        <meta property="twitter:description" content="AnythingLLM | Your personal LLM trained on anything" >
        <meta property="twitter:image" content="https://raw.githubusercontent.com/Mintplex-Labs/anything-llm/master/images/promo.png" >
        <link rel="icon" href="/favicon.png" >
        <link rel="apple-touch-icon" href="/favicon.png" >
        <script type="module" crossorigin src="/index.js"></script>
        <link rel="stylesheet" href="/index.css">
      </head>
      <body>
        <div id="root" class="h-screen"></div>
      </body>
    </html>
    ```

## 应用案例 3：DeepSeek-R1 一键部署

1. 准备一个 openEuler 环境（22.03-LTS-SPX、24.03-LTS-SPX），8B 模型的建议规格大于 8U16G。

2. 下载 oedp 命令行工具，并用 yum 安装。

   ````bash
   wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.1-0.oe2403sp2.noarch.rpm
   yum install -y oedp-1.1.1-0.oe2403sp2.noarch.rpm
   ````

3. 获取并初始化`DeepSeek-R1`插件。

   ````bash
   oedp repo update
   oedp init deepseek-r1
   ````

4. 根据实际情况修改 deepseek-r1/config.yaml。用户可以直接使用这里的示例，不需要任何修改。

   ````yaml
   all:
     hosts:
       # 本地部署 或 远端部署 二选一
       # ================ 本地部署 =====================
       localhost:
         ansible_connection: local
       # ================ 远端部署 =====================
       # host1:
       #   ansible_host: 127.0.0.1      # 远端IP
       #   ansible_port: 22             # 端口号
       #   ansible_user: root           # 用户名
       #   ansible_password: PASSWORD   # 密码
     vars:
       deepseek_version: 8b
       # ollama 官方下载地址: https://ollama.com/download/ollama-linux-amd64.tgz，注意区分amd64和arm64
       # 为提高下载速度，已暂存在 OEPKGS 服务器上
       ollama_download: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/2025.0330/ollama-linux-amd64.tgz
       ollama_download_path: /tmp     # 下载的目标路径
       # 模型文件下载地址: https://www.modelscope.cn/models/unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/master/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
       # 为提高下载速度，已暂存在 OEPKGS 服务器上
       modelfile_download: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/2025.0330/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
       modelfile_download_path: /tmp  # 下载的目标路径
       # 模型参数
       parameter:
         temperature: 0.7
         top_p: 0.7
         top_k: 30
         num_ctx: 4096
         num_thread: 8    # 线程数，建议不超过 CPU 核数
         num_gpu: 0       # GPU数  0 for none, -1 for all.
       
       ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
   ````

5. 一键触发 DeepSeek-R1 自动化部署，oeDeploy 工具会下载所需的文件，自动安装部署，并完成对 DeepSeek-R1 的配置。

   ````bash
   oedp run install -p deepseek-r1  # -p <tar.gz解压后的路径>
   ````

6. 在部署完成后的节点上，打开 DeepSeek-R1 交互终端，开始对话。

   ````bash
   ollama run deepseek-r1:8b
   ````

## 应用案例 4：EulerCopilot 一键部署

### 前提条件

1. 组件介绍

   | 组件                      | 端口                      | 说明         |
       |-------------------------|-------------------------|------------|
   | euler-copilot-framework | 8002（内部端口）             | 智能体框架服务    |
   | euler-copilot-web       | 8080                    | 智能体前端界面    |
   | euler-copilot-rag       | 9988（内部端口）             | 检索增强服务     |
   | authhub-backend-service | 11120 （内部端口）            | 鉴权服务后端     |
   | authhub-web-service     | 8000                    | 鉴权服务前端     |
   | mysql                   | 3306（内部端口）             | MySQL数据库   |
   | redis                   | 6379（内部端口）             | Redis数据库   |
   | minio                   | 9000（内部端口） 9001（外部部端口） | minio数据库   |
   | mongo                   | 27017（内部端口）            | mongo数据库   |
   | postgres                | 5432（内部端口）             | 向量数据库      |
   | secret_inject           | 无                       | 配置文件安全复制工具 |

2. 软件要求

   | 类型     | 版本要求                             | 说明                                                        |
       |--------|----------------------------------|-----------------------------------------------------------|
   | 操作系统   | openEuler 22.03 LTS 及以上版本        | 无                                                         |
   | K3s    | >= v1.30.2，带有 Traefik Ingress 工具 | K3s 提供轻量级的 Kubernetes 集群，易于部署和管理                          |
   | Helm   | >= v3.15.3                       | Helm 是一个 Kubernetes 的包管理工具，其目的是快速安装、升级、卸载 EulerCopilot 服务 |
   | python | >= 3.9.9                         | python3.9.9 以上版本为模型的下载和安装提供运行环境                           |

3. 硬件要求

   | 硬件资源     | 服务器（最小要求）                   | 服务器（推荐）                 |
       |----------|-----------------------------|-------------------------|
   | CPU      | 4 核心                        | 16 核心及以上                |
   | RAM      | 4 GB                        | 64 GB                   |
   | 存储       | 32 GB                       | 64G                     |
   | 大模型名称    | deepseek-llm-7b-chat        | DeepSeek-R1-Llama-8B    |                          
   | 显存（GPU） | 8 GB（NVIDIA RTX A4000, 1个） | 16 GB（NVIDIA A100, 2个） |

   **注意**：

    - 若无 GPU 或 NPU 资源，建议通过调用 OpenAI 接口的方式来实现功能。
    - 调用第三方 OpenAI 接口的方式不需要安装高版本的 python (>=3.9.9)。
    - 如有 k8s 集群环境，则不需要单独安装 k3s，要求 version >= 1.28。

4. 网络要求

    - 可访问 hub.oepkgs.net
    - 可访问 modelscope.cn
    - 开放端口：80/443/

5. 域名要求

   为确保 EulerCopilot 的正确部署和使用，请准备以下两个服务的域名：authhub、eulercopilot。这些子域名需属于同一个主域名下，例如
   `www.eulercopilot.local`、`authhub.eulercopilot.local`。

   您可以通过两种方式来完成这项准备工作：

    - **预先申请域名**：为每个服务（AuthHub、Euler Copilot）分别注册上述格式的子域名。
    - **本地配置**：如果是在开发或测试环境中，您可以直接在本地 Windows 主机文件中进行配置。打开位于
      `C:\Windows\System32\drivers\etc\hosts` 的文件，并添加相应的条目以映射这些子域名到本地或特定的 IP 地址，例如：

       ```bash
       172.0.0.1 authhub.eulercopilot.local
       172.0.0.1 www.eulercopilot.local
       ```

### 部署过程

1. 安装 oeDeploy 工具。

    ```shell
    wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.1-0.oe2403sp2.noarch.rpm
    yum install -y oedp-1.1.1-0.oe2403sp2.noarch.rpm
    ```

2. 获取并初始化 EulerCopilot 插件。

    ```shell
    oedp repo update
    oedp init euler-copilot
    ```

3. 根据实际情况修改 `config.yaml` 文件，示例如下：

    ```yaml
    all:
      hosts:
        host1:
          # 节点空余内存需要大于 16G，建议规格 32G 以上
          # 部署节点 IP
          ansible_host: HOST_IP
          # 部署节点 SSH 端口
          ansible_port: 22
          # 部署节点用户
          ansible_user: root  # 目前仅支持 root 用户
          # 部署节点密码
          ansible_password: PASSWORD

      vars:
        ansible_ssh_common_args: '-o StrictHostKeyChecking=no'

        # 部署日志目录
        log_dir: "/var/log/deploy-euler-copilot"

        # 源码仓库配置
        repo_config:
          # 源码 url
          url: "https://gitee.com/openeuler/euler-copilot-framework.git"
          # 源码仓放置目录
          dest_dir: "/opt/euler-copilot-framework"
          # 指定分支、tag 和 commit
          version: "release-0.9.5"
          # 是否覆盖本地修改
          force: yes

        # 模型配置
        models:
          # 用于问答的大模型；需要为 OpenAI 兼容接口
          answer:
            # [必填] 接口 URL（无需带上“v1”后缀）
            endpoint: https://api.deepseek.com
            # [必填] 接口 API Key；默认置空
            key: sk-xxx
            # [必填] 模型名称
            name: deepseek-chat
            # [必填] 模型最大上下文数；建议 >= 8192
            ctxLength: 8192
            # 模型最大输出长度，建议 >= 2048
            maxTokens: 8192
          # 用于 Function Call 的模型；建议使用特定推理框架
          functionCall:
            # 推理框架类型，默认为 ollama
            # 可用的框架类型：["vllm", "sglang", "ollama", "openai"]
            backend: openai
            # 模型地址；不填则与问答模型一致
            endpoint: https://dashscope.aliyuncs.com/compatible-mode/v1
            # API Key；不填则与问答模型一致
            key: sk-xxx
            # 模型名称；不填则与问答模型一致
            name: qwen-plus
            # 模型最大上下文数；不填则与问答模型一致
            ctxLength:
            # 模型最大输出长度；不填则与问答模型一致
            maxTokens:
          # 用于数据向量化（Embedding）的模型
          embedding:
            # 推理框架类型，默认为 openai
            # [必填] Embedding 接口类型：["openai", "mindie"]
            type: openai
            # [必填] Embedding URL（需要带上“v1”后缀）
            endpoint: https://api.siliconflow.cn/v1
            # [必填] Embedding 模型 API Key
            key: sk-xxx
            # [必填] Embedding 模型名称
            name: BAAI/bge-m3
    ```

4. 一键部署：

    ```shell
    oedp run install -p ./euler-copilot
    ```

5. 验证安装：

   您可以参考 [此文档](https://e.gitee.com/open_euler/repos/openeuler/euler-copilot-framework/blob/master/docs/user-guide/%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97/%E7%BD%91%E7%BB%9C%E7%8E%AF%E5%A2%83%E4%B8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97.md#%E9%AA%8C%E8%AF%81%E5%AE%89%E8%A3%85) 来验证安装是否成功。

6. 一键卸载：

    ```shell
    oedp run uninstall -p ./euler-copilot
    ```

## 应用案例 5：KubeRay 一键部署

### 环境准备

1. 部署 Kubernetes 集群：

   在目标集群机器上部署 Kubernetes 1.31.1，此处以 1 master + 2 worker 的标准 K8S 集群为例，其中 master 节点的 IP 为 192.168.1.101。可使用`kubernetes-1.31.1`插件进行自动化部署。

2. 安装 Helm：

   在 master 节点上安装 Helm，可使用`helm-3.9.0`插件进行自动化安装。

### 部署 KubeRay

1. 获取`kuberay`插件：

   使用以下命令，获取并初始化`kuberay`插件。

    ```shell
    oedp repo update
    oedp init kuberay
    ```

2. 修改`config.yaml`：

   以下是`kuberay/config.yaml`的示例，根据实际情况修改此文件。

    ```yaml
    all:
      hosts:
        host1:
          ansible_host: 192.168.1.101      # master 节点的 IP
          ansible_port: 22                 # ssh 的端口
          ansible_user: root               # ssh 的用户，非root用户需要 sudo 权限
          ansible_password: PASSWORD       # 上述用户的密码
      vars:
        temp_path: /tmp
        namespace: kuberay                 # 命名空间
        version: 1.2.2                     # KubeRay chart 的版本

        helm_repo_name: "kuberay"          # 本地 Helm 仓库别名
        helm_repo_url: "https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/2025.0330/kuberay-helm"

        kuberay_operator_values_file: ""
        # 以上配置项 kuberay_operator_values_file 为高级配置：指定一个 values 文件，用于自定义 
        # KubeRay operator 组件的安装。需填写绝对路径，若留空，则采用以下配置：
        kuberay_operator_values:
          repository: "hub.oepkgs.net/oedeploy/quay.io/kuberay/operator" # KubeRay operator docker 镜像 url
          tag: v1.2.2                      # KubeRay operator docker 仓库 tag

        ray_cluster_values_file: ""
        # 以上配置项 ray_cluster_values_file 为高级配置：指定一个 values 文件，用于自定义 
        # Ray 组件的安装。需填写绝对路径，若留空，则采用以下配置：
        ray_cluster_values:
          repository: "hub.oepkgs.net/oedeploy/rayproject/ray-with-pytorch" # Ray docker 镜像 url
          tag: 2.9.0                       # Ray docker 仓库 tag；使用默认 docker 源时，x86 为 2.9.0, arm 为 2.9.0-aarch64；具体的 tag 请至配置的仓库确认
          head:                            # 头节点资源
            cpu: "1"
            memory: "2G"
          worker:                          # 工作节点资源
            num: 1
            cpu: "1"
            memory: "1G"
        training:                          # 模型训练参数
          pip: "https://pypi.tuna.tsinghua.edu.cn/simple"
          batch_size: 1024
          epoch: 5
    ```

3. 执行自动化部署：

   在插件目录下执行`oedp run install`，或在任意位置执行`oedp run install -p [插件目录]`，即可完成自动化部署 KubeRay。

### 查看 Dashboard

1. 查询对应端口：

   在 master 节点，使用`kubectl get svc -A`命令查看端口映射：

    ````bash
    NAMESPACE     NAME                           TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                                                                       AGE
    default       kubernetes                     ClusterIP   10.96.0.1       <none>        443/TCP                                                                       24h
    kube-system   kube-dns                       ClusterIP   10.96.0.10      <none>        53/UDP,53/TCP,9153/TCP                                                        24h
    kuberay       kuberay-operator               ClusterIP   10.96.175.101   <none>        8080/TCP                                                                      9h
    kuberay       ray-cluster-kuberay-head-svc   NodePort    10.96.168.232   <none>        10001:32414/TCP,8265:31457/TCP,8080:31582/TCP,6379:31938/TCP,8000:32102/TCP   9h
    ````

   其中 8265 对应的端口，即为 Dashboard 的端口。

2. 打开 Dashboard 页面：
   使用 `http://ip:port/` 链接，即可打开 Dashboard 页面，查看 Ray Job / Serve / Cluster 及资源、日志等信息。其中 IP 为 master 节点 IP，port 为 3.1 中 8265 对应的端口。

### Demo 1：基于 FashionMNIST 数据集的 MLP 模型训练推理

1. 已完成 KubeRay 部署，Pod 资源要求至少 4U。

2. 在 master 节点，执行以下命令，即可一键自动完成模型训练、推理。

    ````bash
    oedp run train -p kuberay
    ````

### Demo 2：单 Pod 与多 Pod 运行同个训练模型的时间对比

在 Kuberay 部署前，通过修改 config.yaml，进行 Pod 资源配置。

1. 将单 Pod 的资源设置为：

    ````bash
    head:
      cpu: "7"
      memory: "14G"
    worker:
      num: 0
    ````

   然后执行：

    ````bash
    oedp run install -p kuberay
    oedp run train -p kuberay
    ````

2. 将多 Pod 的资源设置为：

    ````bash
    head:
      cpu: "7"
      memory: "14G"
    worker:
      num: 2
      cpu: "5"
      memory: "10G"
    ````

   然后执行：

    ````bash
    oedp run install -p kuberay
    oedp run train -p kuberay
    ````

3. 对比两者运行时间：

   该条件下，单 Pod 运行时间约为 25s，多 Pod 运行时间约为 67s。

## 应用案例 6：Pytorch 一键部署

1. 准备一个 k8s 集群。

2. 下载 oedp 命令行工具，并用 yum 安装。如有更新的 oedp 版本，可以选择新版本。

   ````bash
   wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.1-0.oe2403sp2.noarch.rpm
   yum install -y oedp-1.1.1-0.oe2403sp2.noarch.rpm
   ````

3. 获取并初始化`pytorch`插件。

    ```shell
    oedp repo update
    oedp init pytorch
    ```

4. 根据实际情况，修改 config.yaml。请确保目标节点为 k8s 的 master 节点。`kubectl_apply`需要与 workspace 下的 playbook 对应。

5. 一键部署：

   ````bash
   oedp run install -p pytorch  # -p <插件目录>
   ````

6. 一键卸载：

   ````bash
   oedp run uninstall -p pytorch  # -p <插件目录>
   ````

### Demo 1：部署并打印 PyTorch 信息

1. 根据实际情况，修改 config.yaml。以下为示例：

      ````yaml
      all:
        hosts:
          localhost:
            ansible_connection: local
        vars:
          ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
          # ================ demo 1: pytorch with http.server =====================
          kubectl_apply: pytorch-deployment.yaml
          namespace: pytorch-namespace
          replicas: 1
          containers:
            http:
              name: http-container
              image: hub.oepkgs.net/oedeploy/pytorch/pytorch:latest  # amd64
              # image: hub.oepkgs.net/oedeploy/pytorch/torchserve:latest-arm64  # arm64
            workspace_mount: /tmp
          service:
            port: 8080
            target_port: 8080
            node_port: 30699
          training:
            epoch: 2
      ````

2. 执行一键部署。

    ```shell
    oedp run install -p pytorch
    ```

3. 查看 pod。

    ````bash
    kubectl get pods -n pytorch-namespace
    ````

    ````
    NAME                                 READY   STATUS    RESTARTS   AGE
    pytorch-deployment-db5d59bcb-ptqnp   1/1     Running   0          15m
    ````

4. 查看端口映射。

    ````bash
    kubectl get svc -n pytorch-namespace
    ````

    ````
    NAME              TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
    pytorch-service   NodePort   10.96.50.156   <none>        80:30699/TCP   15m
    ````

5. 访问网页。

    ````text
    http://x.x.x.x:30699/  # master所在节点
    ````

6. 进入容器。

    ````bash
    kubectl exec -n pytorch-namespace -it pytorch-deployment-db5d59bcb-ptqnp -- /bin/bash
    ````

7. 打印 PyTorch 信息。

    ````bash
    python -c "import torch; print(torch.__version__); print(torch.tensor([1.0, 2.0, 3.0]) + torch.tensor([4.0, 5.0, 6.0]))"
    ````

### Demo 2：基于 MNIST 数据集的轻量 CNN 模型训练

1. 基于 demo 1 已完成 PyTorch 部署。

2. 一键自动完成模型训练。

    ````bash
    oedp run train -p pytorch  # -p <插件目录>
    ````

   回显形如：

    ````bash
    ......  
    TASK [Display training output] *****************************************************************************************************************************************************************************************************************
    ok: [localhost] => {
      "msg": [
        "Train Epoch: 0 [0/60000]\tLoss: 2.3114",
        "Train Epoch: 0 [6400/60000]\tLoss: 0.3884",
        "Train Epoch: 0 [12800/60000]\tLoss: 0.1483",
        "Train Epoch: 0 [19200/60000]\tLoss: 0.0510",
        "Train Epoch: 0 [25600/60000]\tLoss: 0.1151",
        "Train Epoch: 0 [32000/60000]\tLoss: 0.0191",
        "Train Epoch: 0 [38400/60000]\tLoss: 0.0690",
        "Train Epoch: 0 [44800/60000]\tLoss: 0.1995",
        "Train Epoch: 0 [51200/60000]\tLoss: 0.0417",
        "Train Epoch: 0 [57600/60000]\tLoss: 0.1821",
        "Test Accuracy: 9862/10000 (98.62%)",
        "Train Epoch: 1 [0/60000]\tLoss: 0.0052",
        ......
        "Train Epoch: 1 [57600/60000]\tLoss: 0.0115",
        "Test Accuracy: 9877/10000 (98.77%)"
      ]
    }
    ````

## 应用案例 7：TensorFlow 一键部署

1. 准备一个 k8s 集群。

2. 下载 oedp 命令行工具，并用 yum 安装。如有更新的 oedp 版本，可以选择新版本。

   ````bash
   wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.1-0.oe2403sp2.noarch.rpm
   yum install -y oedp-1.1.1-0.oe2403sp2.noarch.rpm
   ````

3. 获取并初始化`tensorflow`插件。

    ```shell
    oedp repo update
    oedp init tensorflow
    ```

4. 根据实际情况，修改 config.yaml。请确保目标节点为 k8s 的 master 节点。`kubectl_apply`需要与 workspace 下的 playbook 对应。

5. 一键部署：

   ````bash
   oedp run install -p tensorflow  # -p <插件目录>
   ````

6. 一键卸载：

   ````bash
   oedp run uninstall -p tensorflow  # -p <插件目录>
   ````

### Demo 1: TensorFlow with Jupyter

1. 编辑 config.yaml 文件。

    ````yaml
    all:
      hosts:
        localhost:
          ansible_connection: local
      
      vars:
        ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
    
        kubectl_apply: tensorflow-deployment.yaml
        namespace: tensorflow-namespace
        replicas: 1
        containers:
          name: tensorflow-jupyter
          image: hub.oepkgs.net/oedeploy/tensorflow/tensorflow:latest-jupyter  # amd64 only
          command: ["jupyter", "notebook", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
        service:
          name: tensorflow-service
          port: 80
          target_port: 8888
          node_port: 30088
    ````

2. 查看 pod 状态。

    ````bash
    kubectl get pods -n tensorflow-namespace
    ````

    ````
    NAME                                             READY   STATUS    RESTARTS   AGE
    tensorflow-deployment-75b85948d8-w2n7b           1/1     Running   0          4m1s
    ````

3. 进入 pod 容器，会有一个很明显的 TensorFlow 大字提示。

    ````bash
    kubectl exec -n tensorflow-namespace -it tensorflow-deployment-75b85948d8-w2n7b -- /bin/bash
    ````

4. 打印 TensorFlow 信息。

    ````bash
    python -c "import tensorflow as tf; print(tf.__version__)"
    ````

5. 打开 Jupyter 界面。

    ````bash
    http://x.x.x.x:30088/  # master 所在节点
    ````

### Demo 2：分布式部署训练集群

1. 编辑 config.yaml 文件。

    ````yaml
    all:
      hosts:
        localhost:
          ansible_connection: local
      
      vars:
        ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
        
        kubectl_apply: tensorflow-distributed.yaml
        namespace: tensorflow-namespace
        ps:
          replicas: 2
          containers:
            name: tensorflow-ps
            image: hub.oepkgs.net/oedeploy/tensorflow/tensorflow:latest  # amd64 only
          service:
            name: tensorflow-ps-service
            port: 2222
            target_port: 2222
        worker:
          replicas: 2
          containers:
            name: tensorflow-worker
            image: hub.oepkgs.net/oedeploy/tensorflow/tensorflow:latest  # amd64 only
          service:
            name: tensorflow-worker-service
            port: 2222
            target_port: 2222
    ````

2. 查看 pod 状态。

    ````bash
    kubectl get pods -n tensorflow-namespace
    ````

    ````
    NAME                                 READY   STATUS    RESTARTS   AGE
    tensorflow-ps-fdddfdb5f-8fc98        1/1     Running   0          2m59s
    tensorflow-ps-fdddfdb5f-dgqm9        1/1     Running   0          2m59s
    tensorflow-worker-6cd8947b75-gxcnq   1/1     Running   0          2m59s
    tensorflow-worker-6cd8947b75-wbt57   1/1     Running   0          2m59s
    ````

    ````bash
    kubectl logs tensorflow-ps-fdddfdb5f-8fc98 -n tensorflow-namespace
    ````

    ````
    2025-02-07 09:25:24.882206: I tensorflow/core/util/port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
    2025-02-07 09:25:24.915813: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
    To enable the following instructions: AVX2 AVX512F AVX512_VNNI FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
    TensorFlow version: 2.18.0
    Environment variables: environ({'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'tensorflow-ps-fdddfdb5f-8fc98', 'DEBIAN_FRONTEND': 'noninteractive', 'LANG': 'C.UTF-8', 'TF_CONFIG': '{\n  "cluster": {\n    "ps": ["tensorflow-ps:2222"],\n    "worker": ["tensorflow-worker-0:2222", "tensorflow-worker-1:2222"]\n  },\n  "task": {"type": "ps", "index": 0}\n}\n', 'KUBERNETES_PORT_443_TCP_PROTO': 'tcp', 'TENSORFLOW_PS_PORT_2222_TCP_PROTO': 'tcp', 'TENSORFLOW_WORKER_SERVICE_PORT': '2222', 'TENSORFLOW_WORKER_PORT': 'tcp://10.96.56.106:2222', 'KUBERNETES_SERVICE_HOST': '10.96.0.1', 'KUBERNETES_PORT_443_TCP_PORT': '443', 'TENSORFLOW_PS_PORT_2222_TCP_PORT': '2222', 'TENSORFLOW_WORKER_PORT_2222_TCP_ADDR': '10.96.56.106', 'TENSORFLOW_WORKER_SERVICE_HOST': '10.96.56.106', 'TENSORFLOW_WORKER_PORT_2222_TCP_PROTO': 'tcp', 'KUBERNETES_SERVICE_PORT': '443', 'KUBERNETES_SERVICE_PORT_HTTPS': '443', 'KUBERNETES_PORT': 'tcp://10.96.0.1:443', 'KUBERNETES_PORT_443_TCP': 'tcp://10.96.0.1:443', 'TENSORFLOW_PS_PORT_2222_TCP': 'tcp://10.96.88.2:2222', 'TENSORFLOW_PS_PORT_2222_TCP_ADDR': '10.96.88.2', 'TENSORFLOW_WORKER_PORT_2222_TCP_PORT': '2222', 'KUBERNETES_PORT_443_TCP_ADDR': '10.96.0.1', 'TENSORFLOW_PS_SERVICE_HOST': '10.96.88.2', 'TENSORFLOW_PS_SERVICE_PORT': '2222', 'TENSORFLOW_PS_PORT': 'tcp://10.96.88.2:2222', 'TENSORFLOW_WORKER_PORT_2222_TCP': 'tcp://10.96.56.106:2222', 'HOME': '/root', 'ENABLE_RUNTIME_UPTIME_TELEMETRY': '1', 'TF2_BEHAVIOR': '1', 'TPU_ML_PLATFORM': 'Tensorflow', 'TPU_ML_PLATFORM_VERSION': '2.18.0'})
    This is the parameter server.
    [2025-02-07 09:25:26.288107] Parameter server is running...
    [2025-02-07 09:26:26.288219] Parameter server is running...
    [2025-02-07 09:27:26.288358] Parameter server is running...
    [2025-02-07 09:28:26.288519] Parameter server is running...
    ````

3. 卸载 pod。

    ````bash
    kubectl delete -f tensorflow-distributed.yaml
    ````
