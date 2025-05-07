# 使用 oeDeploy 部署AnythingLLM
1、下载 oedp 命令行工具，并用 yum 安装。如有更新的 oedp 版本，可以选择新版本。

   ```bash
   # x86_64:
   # aarch64:
   ```

3. 根据实际情况，修改 config.yaml。确保部署节点网络正常

4. 一键部署
   ````bash
   oedp run install -p angthingLLM  # -p <插件目录>
   ````

5. 一键卸载
   ````bash
   oedp run uninstall -p angthingLLM  # -p <插件目录>
   ````



# demo

## demo 1: 部署并打印 PyTorch 信息
- config.yaml
  ````yaml
  all:
  hosts:
    host1:
      ansible_host: 192.168.124.17   # 远端IP
      ansible_port: 22             # 端口号
      ansible_user: root           # 用户名
      ansible_password: passwd   # 密码

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
- 进入容器并测试anythingLLM 服务
    * 进入容器
    ````bash
    docker exec -it anythinglLLM-container /bin/bash
    ````
    * 测试anythingLLM 服务

    ````bash
    curl localhost:3001
    ````
  
- 部署环境测试anythingLLM 服务
  ```bash
   curl 192.168.124.17:3001/ curl localhost:3001
  ```
- 正常返回如下
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