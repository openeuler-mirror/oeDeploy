
# Quickly Deploying DeepSeek-R1 Using oeDeploy

1. Prepare an openEuler environment (22.03-LTS-SPX or 24.03-LTS-SPX). It is recommended that the specifications of the 8B model be greater than 8U16G.

2. Download the oedp command line tool and install it using yum.

   ````bash
   wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.0-3.oe2403sp2.noarch.rpm
   yum install -y oedp-1.1.0-3.oe2403sp2.noarch.rpm
   ````

3. Obtain and initialize the `DeepSeek-R1` extension.

   ````bash
   oedp repo update
   oedp init deepseek-r1
   ````

4. Modify the `deepseek-r1/config.yaml` file as required. You can directly use the example here without modification.

   ````yaml
   all:
     hosts:
       # Local or remote deployment
       # ================ local deployment =====================
       localhost:
         ansible_connection: local
       # ================ remote deployment =====================
       # host1:
       #   ansible_host: 127.0.0.1 # Remote IP address
       #   ansible_port: 22 #Port number
       #   ansible_user: root # Username
       #   ansible_password: "" # Password
     vars:
       deepseek_version: 8b
       # Official download address of Ollama: https://ollama.com/download/ollama-linux-amd64.tgz. Note the difference between AMD64 and ARM64.
       # To increase the download speed, the file is temporarily stored on the OEPKGS server.
       ollama_download: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/2025.0330/ollama-linux-amd64.tgz
       ollama_download_path: /tmp # Download path
       # Model file download address: https://www.modelscope.cn/models/unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/master/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
       # To increase the download speed, the file is temporarily stored on the OEPKGS server.
       modelfile_download: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/2025.0330/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf
       modelfile_download_path: /tmp # Download path
       # Model parameters
       parameter:
         temperature: 0.7
         top_p: 0.7
         top_k: 30
         num_ctx: 4096
         num_thread: 8 # Number of threads. It is recommended that the number be less than or equal to the number of CPU cores.
         num_gpu: 0 # Number of GPUs. 0 for none, -1 for all.
       
       ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
   ````

5. Start the automatic deployment of DeepSeek-R1 in one-click mode. The oeDeploy tool will download the required files, automatically install and deploy DeepSeek-R1, and complete the configuration.

   ````bash
   oedp run install -p deepseek-r1  # -p <tar.gz path after decompression >
   ````

6. On the deployed node, open the DeepSeek-R1 client to start a conversation.

   ````bash
   ollama run deepseek-r1:8b
   ````
