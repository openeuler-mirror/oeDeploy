# 一键部署 EulerCopilot 用户指导

## 1. 前提条件

### 1.1. 组件介绍

| 组件                      | 端口                      | 说明         |
|-------------------------|-------------------------|------------|
| euler-copilot-framework | 8002 (内部端口)             | 智能体框架服务    |
| euler-copilot-web       | 8080                    | 智能体前端界面    |
| euler-copilot-rag       | 9988 (内部端口)             | 检索增强服务     |
| authhub-backend-service | 11120 (内部端口)            | 鉴权服务后端     |
| authhub-web-service     | 8000                    | 鉴权服务前端     |
| mysql                   | 3306 (内部端口)             | MySQL数据库   |
| redis                   | 6379 (内部端口)             | Redis数据库   |
| minio                   | 9000 (内部端口) 9001(外部部端口) | minio数据库   |
| mongo                   | 27017 (内部端口)            | mongo数据库   |
| postgres                | 5432 (内部端口)             | 向量数据库      |
| secret_inject           | 无                       | 配置文件安全复制工具 |

### 1.2. 软件要求

| 类型     | 版本要求                             | 说明                                                        |
|--------|----------------------------------|-----------------------------------------------------------|
| 操作系统   | openEuler 22.03 LTS 及以上版本        | 无                                                         |
| K3s    | >= v1.30.2，带有 Traefik Ingress 工具 | K3s 提供轻量级的 Kubernetes 集群，易于部署和管理                          |
| Helm   | >= v3.15.3                       | Helm 是一个 Kubernetes 的包管理工具，其目的是快速安装、升级、卸载 EulerCopilot 服务 |
| python | >= 3.9.9                         | python3.9.9 以上版本为模型的下载和安装提供运行环境                           |

### 1.3. 硬件要求

| 硬件资源     | 服务器（最小要求）                   | 服务器（推荐）                 |
|----------|-----------------------------|-------------------------|
| CPU      | 4 核心                        | 16 核心及以上                |
| RAM      | 4 GB                        | 64 GB                   |
| 存储       | 32 GB                       | 64G                     |
| 大模型名称    | deepseek-llm-7b-chat        | DeepSeek-R1-Llama-8B    |                          
| 显存 (GPU) | 8 GB (NVIDIA RTX A4000, 1个) | 16 GB (NVIDIA A100, 2个) |

**注意**：

1. 若无 GPU 或 NPU 资源，建议通过调用 OpenAI 接口的方式来实现功能。
2. 调用第三方 OpenAI 接口的方式不需要安装高版本的 python (>=3.9.9)
3. 如果k8s集群环境，则不需要单独安装k3s，要求version >= 1.28

### 1.4. 网络要求：

- 可访问 hub.oepkgs.net
- 可访问 modelscope.cn
- 开放端口：80/443/

### 1.5. 域名要求

为确保 EulerCopilot 的正确部署和使用，请准备以下两个服务的域名：authhub、eulercopilot。这些子域名需属于同一个主域名下，例如
`www.eulercopilot.local`,`authhub.eulercopilot.local `

您可以通过两种方式来完成这项准备工作：

- **预先申请域名**：为每个服务（AuthHub、Euler Copilot）分别注册上述格式的子域名。
- **本地配置**：如果是在开发或测试环境中，您可以直接在本地Windows主机文件中进行配置。打开位于
  `C:\Windows\System32\drivers\etc\hosts` 的文件，并添加相应的条目以映射这些子域名到本地或特定的IP地址，例如：

```bash
172.0.0.1 authhub.eulercopilot.local
172.0.0.1 www.eulercopilot.local
```

## 2. 一键部署

### 2.1. 安装 oeDeploy 工具

```shell
yum install -y oedp-xxx.rpm
```

### 2.2. 修改配置文件

获取插件并进入插件目录：

```shell
cd xxx/euler-copilot
```

根据实际情况修改 `config.yaml` 文件，示例如下：

```yaml
all:
  hosts:
    host1:
      # 部署节点 IP
      ansible_host: HOST_IP
      # 部署节点 SSH 端口
      ansible_port: PORT
      # 部署节点用户
      ansible_user: USER
      # 部署节点密码
      ansible_password: PASSWORD

  vars:
    # 部署日志目录
    log_dir: "/var/log/deploy-euler-copilot"

    # 源码仓库配置
    repo_config:
      # 源码 url
      url: "https://gitee.com/openeuler/euler-copilot-framework.git"
      # 源码仓放置目录
      dest_dir: "/opt/euler-copilot-framework"
      # 指定分支、tag 和 commit
      version: "master"
      # 是否覆盖本地修改
      force: yes

    # 模型配置
    models:
      # 用于问答的大模型；需要为OpenAI兼容接口
      answer:
        # [必填] 接口URL（无需带上“v1”后缀）
        endpoint: https://api.deepseek.com
        # [必填] 接口API Key；默认置空
        key: sk-xxx
        # [必填] 模型名称
        name: deepseek-chat
        # [必填] 模型最大上下文数；建议>=8192
        ctxLength: 8192
        # 模型最大输出长度，建议>=2048
        maxTokens: 8192
      # 用于Function Call的模型；建议使用特定推理框架
      functionCall:
        # 推理框架类型，默认为ollama
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
        # 推理框架类型，默认为openai
        # [必填] Embedding接口类型：["openai", "mindie"]
        type: openai
        # [必填] Embedding URL（需要带上“v1”后缀）
        endpoint: https://api.siliconflow.cn/v1
        # [必填] Embedding 模型API Key
        key: sk-xxx
        # [必填] Embedding 模型名称
        name: BAAI/bge-m3
```

### 2.2 执行一键部署命令

```shell
oedp run install -p ./euler-copilot
```

等待脚本执行完成即可。

## 3. 验证安装

您可以参考[此文档](https://e.gitee.com/open_euler/repos/openeuler/euler-copilot-framework/blob/master/docs/user-guide/%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97/%E7%BD%91%E7%BB%9C%E7%8E%AF%E5%A2%83%E4%B8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97.md#%E9%AA%8C%E8%AF%81%E5%AE%89%E8%A3%85)来验证安装是否成功。

## 4. 一键卸载

在插件目录下，执行以下命令：

```shell
oedp run uninstall -p ./euler-copilot
```

等待脚本执行完成即可。