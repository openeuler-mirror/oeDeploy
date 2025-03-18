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
      ansible_host: 172.0.0.1  # 更换为实际部署机器的IP
      ansible_port: 22
      ansible_user: root
      ansible_password: 123456 # 更换为实际部署机器的登录密码
  vars:
    temp_dir: /tmp
    log_dir: /var/log
    # 如果不指定PyPI源，可以留空
    pypi_index_url: https://mirrors.huaweicloud.com/repository/pypi/simple
    pypi_trusted_host: mirrors.huaweicloud.com
    # 可根据实际需要更换域名
    eulercopilot_domain: "www.eulercopilot.local"
    authhub_domain: "authhub.eulercopilot.local"
    # 选择是否自带部署大模型
    install_ollama: "true"
    deploy_deepseek: "true"
    deploy_embedding: "true"
    # 配置大模型，如果使用自带部署的大模型请不要修改
    models:
      answer:
        # url后不要带有v1/...
        url: http://$host:11434
        key: sk-123456
        name: deepseek-llm-7b-chat:latest
        ctx_length: 8192
        max_tokens: 2048
      embedding:
        url: http://$host:11434
        key: sk-123456
        name: bge-m3:latest
```

### 2.2 执行一键部署命令

```shell
oedp run install
```

等待脚本执行完成即可。

## 3. 验证安装

您可以参考[此文档](https://e.gitee.com/open_euler/repos/openeuler/euler-copilot-framework/blob/master/docs/user-guide/%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97/%E7%BD%91%E7%BB%9C%E7%8E%AF%E5%A2%83%E4%B8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97.md#%E9%AA%8C%E8%AF%81%E5%AE%89%E8%A3%85)来验证安装是否成功。

## 4. 一键卸载

在插件目录下，执行以下命令：

```shell
oedp run uninstall
```

等待脚本执行完成即可。