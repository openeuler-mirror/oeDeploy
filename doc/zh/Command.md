# # `oedp`参数说明

## `oedp`

| 选项          | 选项简写 | 功能说明   |
| ------------- | -------- | ---------- |
| `--version` | `-v`   | 查询版本号 |

## `oedp info`

查看项目的详细信息，默认为当前路径

| 选项                 | 简写   | 是否必需 | 功能说明                 |
| -------------------- | ------ | -------- | ------------------------ |
| `--project [path]` | `-p` | N        | 项目路径，默认为当前路径 |

## `oedp run [action]`

执行项目某个方法，默认为当前路径；`[action]`为插件可使用的方法，可通过 `oedp info`命令查询

| 选项                 | 简写   | 是否必需 | 功能说明                 |
| -------------------- | ------ | -------- | ------------------------ |
| `--project [path]` | `-p` | N        | 项目路径，默认为当前路径 |
| `--debug`          | `-d` | N        | 以debug模式运行          |

## `oedp list`（开发中）

列举源中可用的插件

## `oedp init [plugin]`

插件初始化到指定路径，`[plugin]`可以是插件压缩包路径、插件下载地址、插件名称

- `[plugin]`如果为本地的插件压缩包（以`tar.gz`结尾），则直接初始化到指定路径
- `[plugin]`如果为插件下载地址（以`tar.gz`结尾），则先下载到缓存路径`/var/oedp/plugin/`，再初始化到指定路径
- `[plugin]`如果为插件名称，从已经配置的插件源中查找，下载到缓存路径后初始化到指定路径

| 选项               | 简写 | 是否必需 | 功能说明                                                     |
| ------------------ | ---- | -------- | ------------------------------------------------------------ |
| `--project [path]` | `-p` | N        | 项目路径，若不存在则创建                                     |
| `--dir [path]`     | `-d` | N        | 项目的父路径，若不存在则创建。如果未指定项目路径与父路径，则父路径默认取当前目录。 |
| `--force`          | `-f` | N        | 强制覆盖路径，请谨慎使用；如果路径存在，会先删除该路径中的所有文件，再初始化 |

示例：假设当前路径为家目录`~`，如下5个命令的效果，都是初始化了一个目录为`~/kubernetes-1.31.1`的 oeDeploy 插件

````bash
oedp init kubernetes-1.31.1
oedp init kubernetes-1.31.1.tar.gz
oedp init https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/kubernetes-1.31.1.tar.gz
oedp init kubernetes-1.31.1 -p ~/kubernetes-1.31.1
oedp init kubernetes-1.31.1 -d ~
````

## `oedp repo`

插件源管理。支持本地插件源、远端插件源。

| 选项                 | 功能说明               |
| -------------------- | ---------------------- |
| `list`             | 查询所有已配置的插件源 |
| `update`           | 更新插件索引缓存       |
| `set [name] [url]` | 修改插件源地址         |
| `del [name]`       | 删除插件源             |
| `enable [name]`    | 使能插件源             |
| `disable [name]`   | 去使能插件源           |

插件源配置文件 `/etc/oedp/config/repo/repo.conf`示例

````ini
[openEuler]
url = https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/
enabled = true

[local]
url = file:///root/.oedp/plugins/
enabled = false
````

## `oedp check [action]`

检查项目中指定方法的检查项，默认为当前路径

| 选项                 | 简写   | 是否必需 | 功能说明                 |
| -------------------- | ------ | -------- | ------------------------ |
| `--project [path]` | `-p` | N        | 项目路径，默认为当前路径 |

## `oedp clean`（开发中）

清理所有临时插件文件。

# # `oedp`工具相关文件与路径

| 路径                              | 说明                   |
| --------------------------------- | ---------------------- |
| `/etc/oedp/config/`               | 配置文件路径           |
| `/etc/oedp/config/repo/cache/`    | 插件源索引文件缓存路径 |
| `/etc/oedp/config/repo/repo.conf` | 插件源配置文件         |
| `/usr/lib/oedp/src/`              | 源码路径               |
| `/var/oedp/log/`                  | 日志文件路径           |
| `/var/oedp/plugin/`               | 插件缓存路径           |

# # 插件源

## 格式说明

oeDeploy 支持从可访问的插件源自动获取安装部署插件，并初始化到本地。

插件源的根目录下必须有一个索引文件 `index.yaml`，其描述了当前插件源中所有可访问插件的具体路径。

oeDeploy 提供了脚本 `tools/build_repo/make_repo_index.py`，用于自动生成 `index.yaml`。

`index.yaml`格式如下：

```yaml
---
apiversion: v1
plugins:
- kubernetes-1.31.1:
  - name: kubernetes-1.31.1
    version: 1.0.0-1
    updated: "2025-03-05T10:31:02.608017752+08:00"
    description: oeDeploy pulgin for kubernetes deployment
    icon: https://gitee.com/openeuler/oeDeploy/blob/master/oedp/build/static/oeDeploy.png
    type: app
    sha256sum: 683995d14bbf425f18d1086858f210fc704b1d14edb274382d0e518a5d2a92c1
    size: 1061949301
    urls:
    - https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/kubernetes-1.31.1.tar.gz
  - name: kubernetes-1.31.1
    version: 1.0.0-2
    ...
- pytorch:
  - name: pytorch
    version: 1.0.0-1
    updated: "2025-03-05T10:31:02.608017752+08:00"
    description: oeDeploy pulgin for pytorch deployment
    icon: https://gitee.com/openeuler/oeDeploy/blob/master/oedp/build/static/oeDeploy.png
    type: app
    sha256sum: 3fe0cb97e01ac9af2c1c8d12d12753f82988ab0e39b5878f359829574102c79d
    size: 2373
    urls:
    - https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/pytorch.tar.gz
  ...
...
```

插件字段含义：

| 字段            | 含义                                                                     | 获取方式      |
| --------------- | ------------------------------------------------------------------------ | ------------- |
| `name`        | 插件名称。允许插件名称中带有版本号，表示软件本身的版本，而非插件的版本。 | 读取main.yaml |
| `version`     | 插件版本号。                                                             | 读取main.yaml |
| `updated`     | 插件更新的时间。允许为空。                                               | 读取main.yaml |
| `description` | 插件介绍。允许为空。                                                     | 读取main.yaml |
| `icon`        | 插件图标地址，用于Web端显示。允许为空。                                  | 读取main.yaml |
| `type`        | 插件类型。保留字段，暂不生效。默认值 `app`。                           | 读取main.yaml |
| `sha256sum`   | 插件文件sha256数值，用于下载时的完整性校验。                             | 脚本生成      |
| `size`        | 插件文件大小，单位Bytes。                                                | 脚本生成      |
| `urls`        | 插件下载地址，可以有多个。所有url地址都必须在当前插件源目录的范围内。    | 脚本生成      |

其他字段：

| 字段           | 含义                                                      | 获取方式 |
| -------------- | --------------------------------------------------------- | -------- |
| `apiversion` | 索引文件格式的版本号。保留字段，暂不生效。默认值 `v1`。 | 脚本生成 |

## 插件源构建方式（开发中）

执行如下命令，一键生成索引文件 `index.yaml`：

````bash
python3 make_repo_index.py [plugins_dir] [url_prefix] [output_dir]
````

`plugins_dir`表示当前 Linux 环境下的插件源根目录，脚本会自动识别目录下所有符合条件的 oeDeploy 插件

`url_prefix`表示每个插件源的 url 索引前缀，即对外暴露的插件源根目录

`output_dir`表示索引文件 `index.yaml`输出的目录

例如，当前 Linux 环境上 `/root/build_workspace/storages/plugins`目录中有多个 oeDeploy 插件，同时映射到 `http://x.x.x.x:8080/plugins`，作为文件服务器对外暴露。

执行如下命令，可以在 `/root/build_workspace/storages/plugins`目录下生成一个 `index.yaml`，其中每个插件的 `urls`字段是其在文件服务器上的访问地址。

````bash
python3 make_repo_index.py /root/build_workspace/storages/plugins http://x.x.x.x:8080/plugins /root/build_workspace/storages/plugins
````
