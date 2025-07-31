# 插件源构建方式

执行如下命令，一键生成索引文件 `index.yaml`：

```bash
python3 make_repo_index.py [plugins_dir] [url_prefix] [output_dir] [extra_item]
```

- `plugins_dir`表示当前 Linux 环境下的插件源根目录，脚本会自动识别目录下（包括所有子目录）所有符合条件的 oeDeploy 插件（后缀为.tar.gz的压缩包）。

- `url_prefix`表示每个插件源的 url 索引前缀，即对外暴露的插件源根目录。

- `output_dir`表示索引文件 `index.yaml`输出的目录。

- `extra_item`(可选)表示额外补充项的YAML文件路径，用于合并额外的插件版本信息到索引中。文件格式示例：
  ```yaml
  apiversion: v1
  plugins:
  - anythingLLM:
    - name: anythingLLM
      version: 1.0.1
      updated: 2025-05-15T19:32:52+0800
      author: ''
      url: ''
      description: anythingLLM
      description_zh: ''
      description_en: ''
      readme: ''
      icon: ''
      type: app
      sha256sum: 1be1169f28e02781f2ad2fb6ff732e98d7704a9e097dbfcc25e8480acbc20bbb
      size: 3861
      urls:
      - https:/repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/anythingLLM.tar.gz
  ```

脚本会自动处理以下情况：
1. 合并主目录和额外文件中的插件版本
2. 按版本号从大到小排序
3. 自动去重相同插件名和版本号的条目

例如，当前 Linux 环境上 `/root/build_workspace/storages/plugins`目录中有多个 oeDeploy 插件，同时映射到 `http://x.x.x.x:8080/plugins`，作为文件服务器对外暴露。

未存储在当前环境的oeDeploy插件信息记录在 `/root/build_workspace/storages/extra.yaml`。

执行如下命令，可以在 `/root/build_workspace/storages/plugins`目录下生成一个 `index.yaml`，其中每个插件的 `urls`字段是其在文件服务器上的真实访问地址，可以直接下载。

```bash
python3 make_repo_index.py /root/build_workspace/storages/plugins http://x.x.x.x:8080/plugins /root/build_workspace/storages/plugins /root/build_workspace/storages/extra.yaml
```