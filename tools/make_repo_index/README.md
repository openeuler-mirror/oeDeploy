# 插件源构建方式

执行如下命令，一键生成索引文件 `index.yaml`：

```bash
python3 make_repo_index.py [plugins_dir] [url_prefix] [output_dir]
```

- `plugins_dir`表示当前 Linux 环境下的插件源根目录，脚本会自动识别目录下（包括所有子目录）所有符合条件的 oeDeploy 插件（后缀为.tar.gz的压缩包）。

- `url_prefix`表示每个插件源的 url 索引前缀，即对外暴露的插件源根目录。

- `output_dir`表示索引文件 `index.yaml`输出的目录。

例如，当前 Linux 环境上 `/root/build_workspace/storages/plugins`目录中有多个 oeDeploy 插件，同时映射到 `http://x.x.x.x:8080/plugins`，作为文件服务器对外暴露。

执行如下命令，可以在 `/root/build_workspace/storages/plugins`目录下生成一个 `index.yaml`，其中每个插件的 `urls`字段是其在文件服务器上的真实访问地址，可以直接下载。

```bash
python3 make_repo_index.py /root/build_workspace/storages/plugins http://x.x.x.x:8080/plugins /root/build_workspace/storages/plugins
```