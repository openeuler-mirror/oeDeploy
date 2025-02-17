
# 使用oeDeploy工具快速部署DeepSeek-R1

1. 准备一个openEuler环境（22.03-LTS-SPX、24.03-LTS-SPX），8B模型的建议规格大于8U16G

2. 下载oedp命令行工具，并用yum安装

   ````bash
   # x86_64:
   wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/x86_64/Packages/oedp-1.0.0-20250208.x86_64.rpm
   yum install -y oedp-1.0.0-20250208.x86_64.rpm
   # aarch64:
   wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/aarch64/Packages/oedp-1.0.0-20250208.aarch64.rpm
   yum install -y oedp-1.0.0-20250208.aarch64.rpm
   ````

3. 下载DeepSeek-R1部署插件，并解压到本地
   ````bash
   wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/2025.0330/deepseek-r1.tar.gz
   yum install -y tar
   tar -zxvf deepseek-r1.tar.gz
   ````

4. 根据实际情况修改deepseek-r1/config.yaml。用户可以直接使用这里的示例，不需要任何修改。

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
       # ollama官方下载地址: https://ollama.com/download/ollama-linux-amd64.tgz，注意区分amd64和arm64
       # 为提高下载速度，已暂存在OEPKGS服务器上
       ollama_download: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/2025.0330/ollama-linux-amd64.tgz
       ollama_download_path: /tmp     # 下载的目标路径
       # 模型文件下载地址: https://www.modelscope.cn/models/unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/master/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
       # 为提高下载速度，已暂存在OEPKGS服务器上
       modelfile_download: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/2025.0330/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
       modelfile_download_path: /tmp  # 下载的目标路径
       # 模型参数
       parameter:
         temperature: 0.7
         top_p: 0.7
         top_k: 30
         num_ctx: 4096
         num_thread: 8    # 线程数，建议不超过CPU核数
         num_gpu: 0       # GPU数  0 for none, -1 for all.
       
       ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
   ````

5. 一键触发DeepSeek-R1自动化部署，oeDeploy工具会下载所需的文件，自动安装部署，并完成对DeepSeek-R1的配置
   ````bash
   oedp run install -p deepseek-r1  # -p <tar.gz解压后的路径>
   ````

6. 在部署完成后的节点上，打开DeepSeek-R1交互终端，开始对话
   ````bash
   ollama run deepseek-r1:8b
   ````
