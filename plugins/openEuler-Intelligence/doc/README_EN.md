# Quick Deployment Guide of openEuler Intelligence

## 1. Prerequisites

### 1.1. Component Description

| Component                     | Port                     | Description        |
|-------------------------|-------------------------|------------|
| euler-copilot-framework | 8002 (internal port)            | Intelligent agent framework service   |
| euler-copilot-web       | 8080                    | Intelligent agent frontend   |
| euler-copilot-rag       | 9988 (internal port)            | Retrieval enhancement service    |
| authhub-backend-service | 11120 (internal port)           | Authentication service backend    |
| authhub-web-service     | 8000                    | Authentication service frontend    |
| mysql                   | 3306 (internal port)            | MySQL database  |
| redis                   | 6379 (internal port)            | Redis databases  |
| minio                   | 9000 (internal port) 9001 (external port)| MinIO database  |
| mongo                   | 27017 (internal port)           | Mongo database  |
| postgres                | 5432 (internal port)            | Vector database     |
| secret_inject           | None                      | Secure configuration file copy tool|

### 1.2. Software Requirements

| Type    | Version Requirement                            | Description                                                       |
|--------|----------------------------------|-----------------------------------------------------------|
| OS   | openEuler 22.03 LTS or later       | None                                                        |
| K3s    | v1.30.2 or later, with the Traefik Ingress tool| K3s provides lightweight Kubernetes clusters that are easy to deploy and manage.                         |
| Helm   | v3.15.3 or later                      | Helm is a Kubernetes package management tool designed to quickly install, upgrade, and uninstall the openEuler intelligence service.|
| python | 3.9.9 or later                        | Python 3.9.9 or later provides a runtime environment for downloading and installing models.                          |

### 1.3. Hardware Requirements

| Hardware    | Server (Minimum Requirement)                  | Server (Recommended)                |
|----------|-----------------------------|-------------------------|
| CPU      | 4 cores                       | 16 cores or more               |
| RAM      | 4 GB                        | 64 GB                   |
| Storage      | 32 GB                       | 64 GB                    |
| Model name   | deepseek-llm-7b-chat        | DeepSeek-R1-Llama-8B    |                          
| VRAM memory (GPU)| 8 GB (NVIDIA RTX A4000, 1)| 16 GB (NVIDIA A100, 2)|

**Notes:**

1. If no GPU or NPU resources are available, you are advised to call the OpenAI API to implement the function.
2. To call the third-party OpenAI API, you do not need to install Python of a later version (3.9.9 or later).
3. If the Kubernetes cluster environment is used, you do not need to install k3s separately. The version must be 1.28 or later.

### 1.4. Network Requirements

- hub.oepkgs.net can be accessed.
- modelscope.cn can be accessed.
- Open ports: 80/443/

### 1.5. Domain Name Requirements

To ensure the correct deployment and use of openEuler intelligence, prepare the domain names for the following two services: authhub and eulercopilot. These subdomains must belong to the same primary domain. For example:
`www.eulercopilot.local`,`authhub.eulercopilot.local`

You can complete this preparation in either of the following ways:

- **Applying for domain names in advance**: Register a subdomain name in the preceding format for each service (AuthHub and Euler Copilot).
- **Local configuration**: If you are in a development or testing environment, you can directly configure the subdomain names in the local Windows host file. Open the file located at
  `C:\Windows\System32\drivers\etc\hosts` and add the corresponding entries to map these subdomain names to the local or specific IP addresses. For example:

```bash
172.0.0.1 authhub.eulercopilot.local
172.0.0.1 www.eulercopilot.local
```

## 2. Quick deployment

### 2.1. Installing the oeDeploy Tool

```shell
yum install -y oedp-xxx.rpm
```

### 2.2. Modifying the Configuration File

Obtain the plug-in and go to the plug-in directory.

```shell
cd xxx/openEuler-Intelligence
```

Modify the `config.yaml` file based on the site requirements. The following is an example.

```yaml
all:
  hosts:
    host1:
      # The available memory of the node must be greater than 16 GB. The recommended memory is greater than 32 GB.
      # Deployment node IP address
      ansible_host: HOST_IP
      # SSH port of the deployment node
      ansible_port: 22
      # Deployment node user
      ansible_user: root  # Currently, only the root user is supported.
      # Deployment node password
      ansible_password: ""

  vars:
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'

    # Deployment log directory
    log_dir: "/var/log/deploy-euler-copilot"

    # Source code repository configuration
    repo_config:
      # Source code URL
      url: "https://atomgit.com/openeuler/euler-copilot-framework.git"
      # Source code repository directory
      dest_dir: "/opt/euler-copilot-framework"
      # Specifying the branch, tag, and commit
      version: "release-0.9.5"
      # Whether to overwrite the local modification
      force: yes

    # Model configuration
    models:
      # Model used for Q&A; the API must be compatible with OpenAI.
      answer:
        # [Mandatory] API URL (the suffix "v1" is not required)
        endpoint: https://api.deepseek.com
        # [Mandatory] API key, left empty by default
        key: sk-xxx
        # [Mandatory] Model name
        name: deepseek-chat
        # [Mandatory] Maximum number of contexts in the model, recommended value: ≥ 8192
        ctxLength: 8192
        # Maximum output length of the model, recommended value: ≥ 2048
        maxTokens: 8192
      # Model used for function calls. A specific inference framework is recommended.
      functionCall:
        # Inference framework type, ollama default
        # Available framework types: ["vllm", "sglang", "ollama", "openai"]
        backend: openai
        # Model address. If left blank, the value of this parameter is the same as that of the Q&A model.
        endpoint: https://dashscope.aliyuncs.com/compatible-mode/v1
        # API key. If left blank, the value of this parameter is the same as that of the Q&A model.
        key: sk-xxx
        # Model name. If left blank, the value of this parameter is the same as that of the Q&A model.
        name: qwen-plus
        # Maximum number of contexts of the model. If left blank, the value of this parameter is the same as that of the Q&A model.
        ctxLength:
        # Maximum length of output of the model. If left blank, the value of this parameter is the same as that of the Q&A model.
        maxTokens:
      # Model used for data vectorization (embedding)
      embedding:
        # Inference framework type, openai default
        # [Mandatory] Embedding API type: ["openai", "mindie"]
        type: openai
        # [Mandatory] Embedding URL (the suffix "v1" is required)
        endpoint: https://api.siliconflow.cn/v1
        # [Mandatory] Embedding model API key
        key: sk-xxx
        # [Mandatory] Embedding model name
        name: BAAI/bge-m3
```

### 2.2 Executing the One-Click Deployment Command

```shell
oedp run install -p ./openEuler-Intelligence
```

Wait until the script execution is complete.

## 3. One-Click Uninstallation

Run the following command in the plugin directory.

```shell
oedp run uninstall -p ./openEuler-Intelligence
```

Wait until the script execution is complete.
