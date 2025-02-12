
# 使用oeDeploy工具快速部署DeepSeek-R1

1. 准备一个openEuler环境（22.03-LTS-SPX、24.03-LTS-SPX），建议规格大于4U16G

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

4. 根据实际情况修改deepseek-r1/config.yaml。用户可以只关注有注释的部分，其他保留默认值

   ````yaml
   all:
     hosts:
       host1:
         ansible_host: 127.0.0.1       # 需要部署DeepSeek的节点IP，127.0.0.1则表示本机
         ansible_port: 22              # 节点端口号
         ansible_user: root            # 用户名
         ansible_password: PASSWORD    # 密码
     vars:
       deepseek_version: 8b            # 当前仅支持8b
       ollama_architecture: amd64      # 根据待部署节点的架构填写amd64或arm64
       ollama_download: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/2025.0330/
       ollama_download_path: /tmp
       modelfile_name: DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
       modelfile_download: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/2025.0330/
       modelfile_download_path: /tmp
       parameter:
         temperature: 0.7
         top_p: 0.7
         top_k: 30
         num_ctx: 4096
         num_thread: 16                # 最大线程数量，建议不超过待部署节点的CPU核数
         num_gpu: 0                    # GPU数量，0表示无GPU，-1表示全部GPU
       ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
   ````

5. 一键触发DeepSeek-R1自动化部署，oeDeploy工具会下载所需的文件，自动安装部署，并完成对DeepSeek-R1的配置
   ````bash
   oedp run install -p deepseek-r1  # -p < tar.gz解压后的路径 >
   ````

6. 在部署完成后的节点上，打开DeepSeek-R1交互终端，开始对话
   ````bash
   ollama run deepseek-r1:8b
   ````
