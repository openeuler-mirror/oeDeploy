# Deploying AnythingLLM Using oeDeploy

1. Download the oedp command line tool and install it using yum. If a new oedp version is available, you can use the new version.

   ```bash
   wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/noarch/oedp-1.1.0-3.oe2403sp2.noarch.rpm
   yum install -y oedp-1.1.0-3.oe2403sp2.noarch.rpm
   ```

2. Obtain and initialize the `AnythingLLM` plugin.

    ```bash
    oedp repo update
    oedp init anythingLLM
    ```
   
3. Modify **config.yaml** based on site requirements. Ensure that the network of the deployment node is normal.

4. Perform one-click deployment.

   ```bash
   oedp run install -p angthingLLM  # -p <plugin directory>
   ```

5. Perform one-click uninstallation.

   ```bash
   oedp run uninstall -p angthingLLM # -p <plugin directory>
   ```

# Demo

## Demo 1: Deploying and Printing PyTorch Information

- config.yaml

  ```yaml
  all:
  hosts:
    host1:
      ansible_host: 192.168.124.17   # remote IP address
      ansible_port: 22             # port number
      ansible_user: root           # username
      ansible_password: ""   # password

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
  ```

- Access the container and test the anythingLLM service.
    * Access the container.

    ```bash
    docker exec -it anythinglLLM-container /bin/bash

    ```

    * Test the anythingLLM service.

    ```bash
    curl localhost:3001
    ```
  
- Test the AnythingLLM service in the deployment environment.

  ```bash
   curl 192.168.124.17:3001/ curl localhost:3001
  ```

- In normal case, the following information is returned.

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
