# # `oedp`命令行设计 & 使用说明

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

| 选项               | 简写 | 是否必需 | 功能说明                             |
| ------------------ | ---- | -------- | ------------------------------------ |
| `--project [path]` | `-p` | N        | 项目路径，默认为当前路径             |
| `--debug`          | `-d` | N        | 以debug模式运行                      |
| `--time`           | `-t` | N        | 记录脚本中每个步骤的时间戳与执行用时 |
| `--local`          | `-l` | N        | 部署到本地（并非所有插件都支持）     |

## `oedp list`

列举插件源中可用的插件

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

示例：假设当前路径为家目录`~`，如下5个命令执行后，都是初始化了一个目录为`~/kubernetes-1.31.1`的 oeDeploy 插件

````bash
oedp init kubernetes-1.31.1
oedp init kubernetes-1.31.1.tar.gz
oedp init https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/kubernetes-1.31.1.tar.gz
oedp init kubernetes-1.31.1 -p ~/kubernetes-1.31.1
oedp init kubernetes-1.31.1 -d ~
````

## `oedp repo`

插件源管理。

- 支持本地插件源、远端插件源。
- 插件源不可重名。

| 选项                                                         | 功能说明                                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `list`                                                       | 查询所有已配置的插件源                                       |
| `update`                                                     | 更新插件索引缓存                                             |
| `set [name] [url]`                                           | 增加/修改插件源地址                                          |
| `del [name]`                                                 | 删除插件源                                                   |
| `enable [name]`                                              | 使能插件源                                                   |
| `disable [name]`                                             | 去使能插件源                                                 |
| `make [plugins_dir] [url_prefix] [output_dir] [extra_item]` | 生成插件源索引文件，extra_item参数可选                       |
| `make-local [path]`                                          | 生成本地插件源索引文件，path可选(默认当前目录) |

插件源配置文件 `/etc/oedp/config/repo/repo.conf`示例

````ini
[openEuler]
url = https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/
enabled = true

[local]
url = file:///root/.oedp/plugins/
enabled = false
````

# # `oedp`工具相关文件与路径

| 路径                              | 说明                                                         |
| --------------------------------- | ------------------------------------------------------------ |
| `/etc/oedp/config/`               | 配置文件路径                                                 |
| `/etc/oedp/config/repo/cache/`    | 插件源索引文件缓存路径，每个已经生效的插件源都会生成一个`[name].yaml`文件 |
| `/etc/oedp/config/repo/details`   | 插件配置信息缓存目录（每个插件删除`workspace`后的部分），用于 DevStore 读取图标与 README。 |
| `/etc/oedp/config/repo/repo.conf` | 插件源配置文件                                               |
| `/usr/lib/oedp/src/`              | 源码路径                                                     |
| `/var/oedp/log/`                  | 日志文件路径                                                 |
| `/var/oedp/plugin/`               | 插件缓存路径                                                 |

# # oeDeploy 插件源

## 插件源格式说明 

oeDeploy 支持从可访问的插件源自动获取安装部署插件，并初始化到本地。

插件源的根目录下必须有一个索引文件 `index.yaml`，其描述了当前插件源中所有可访问插件的具体信息，包括下载地址。

oeDeploy 提供了 `oedp repo make` 和 `oedp repo make-local` 命令，用于自动生成 `index.yaml`。

`index.yaml`示例如下：

```yaml
apiversion: v1
plugins:
- anythingLLM:
  - name: anythingLLM
    version: 1.0.0
    updated: 2025-07-26T17:43:28+0800
    author: ''
    url: https://gitee.com/openeuler/oeDeploy/tree/master/plugins/anythingLLM
    description: oeDeploy plugin for anythingLLM fast deployment
    description_zh: 用于anythingLLM快速部署的oeDeploy插件
    description_en: oeDeploy plugin for anythingLLM fast deployment
    readme: ''
    icon: ''
    localhost_available: true
    type: app
    sha256sum: 54f22780afadd02559e4a5bfdf672c6f2af1f17a73fe08fc4e3cd82aeee0cdef
    size: 12820
    urls:
    - https:/repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/anythingLLM.tar.gz
- deepseek-r1:
  - name: deepseek-r1
    version: 1.0.0
    updated: 2025-05-27T21:33:00+0800
    author: ''
    url: ''
    description: deepseek-r1 1.0.0
    description_zh: ''
    description_en: ''
    readme: ''
    icon: ''
    localhost_available: false
    type: app
    sha256sum: 9c991734052aa32c2ca362835115c6f2cb51026226f0aecbfeda134348812408
    size: 4787
    urls:
    - https:/repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/plugins/deepseek-r1.tar.gz
```

首层字段含义：

| 字段         | 含义                                                         |
| ------------ | ------------------------------------------------------------ |
| `plugins`    | 含有多个插件名称（默认字母序排序），一个插件名称中可能包含多个不同版本的插件（默认根据版本号倒序排序） |
| `apiversion` | 索引文件格式的版本号。保留字段，暂不生效。默认值 `v1`。      |

插件字段含义：

| 字段                  | 含义                                                         | 获取方式                        |
| --------------------- | ------------------------------------------------------------ | ------------------------------- |
| `name`                | 插件名称。允许插件名称中带有版本号，表示软件本身的版本，而非插件的版本。 | 与插件压缩包同名（不带.tar.gz） |
| `version`             | 插件版本号，并非所部署软件的版本号。                         | 读取main.yaml                   |
| `updated`             | 插件更新的时间，格式为`%Y-%m-%dT%H:%M:%S%z`。允许为空。      | 插件打包时间                    |
| `author`              | 插件发布者。允许为空。                                       | 读取main.yaml                   |
| `description`         | 插件简介（当多语言简介缺失时，作为缺省值）。允许为空。       | 读取main.yaml                   |
| `description_zh`      | 插件简介（中文，用于检索匹配）。允许为空。                   | 读取main.yaml                   |
| `description_en`      | 插件简介（英文，用于检索匹配）。允许为空。                   | 读取main.yaml                   |
| `icon`                | 插件图标地址，用于Web端显示。允许为空。                      | 读取main.yaml                   |
| `type`                | 插件类型。保留字段，暂不生效。默认值 `app`。                 | 读取main.yaml                   |
| `localhost_available` | 插件是否支持本地单节点部署。允许为空，缺省为`false`。        | 读取main.yaml                   |
| `sha256sum`           | 插件文件sha256数值，用于下载时的完整性校验。                 | sha256计算                      |
| `size`                | 插件文件大小，单位Bytes。                                    | 压缩包实际大小                  |
| `download_urls`       | 插件下载地址，可以有多个。所有url地址都必须在当前插件源目录的范围内。 | 前缀与相对路径的拼接结果        |

## 插件源构建方式

### 方式1：使用 `oedp repo make` 命令

执行如下命令，一键生成索引文件 `index.yaml`：

```bash
oedp repo make [plugins_dir] [url_prefix] [output_dir] [extra_item]
```

- `plugins_dir`表示当前 Linux 环境下的插件源根目录，命令会自动识别目录下（包括所有子目录）所有符合条件的 oeDeploy 插件（后缀为.tar.gz的压缩包）。

- `url_prefix`表示每个插件源的 url 索引前缀，即对外暴露的插件源根目录。

- `output_dir`表示索引文件 `index.yaml`输出的目录。

- `extra_item`(可选)表示额外补充项的YAML文件路径，用于合并额外的插件版本信息到索引中。

命令会自动处理以下情况：

1. 合并主目录和额外文件中的插件版本
2. 按版本号从大到小排序
3. 自动去重相同插件名和版本号的条目

例如，假设当前 Linux 环境上 `/root/build_workspace/storages/plugins`目录中有多个 oeDeploy 插件，且该目录映射到 `http://x.x.x.x:8080/plugins`，作为文件服务器对外暴露。

未存储在当前环境的oeDeploy插件信息记录在 `/root/build_workspace/storages/extra.yaml`。

执行如下命令，可以在 `/root/build_workspace/storages/plugins`目录下生成一个 `index.yaml`，其中每个插件的 `urls`字段是其在文件服务器上的真实访问地址，可以直接下载。

```bash
oedp repo make \
/root/build_workspace/storages/plugins \
http://x.x.x.x:8080/plugins \
/root/build_workspace/storages/plugins \
/root/build_workspace/storages/extra.yaml
```

### 方式2：使用 `oedp repo make-local` 命令

对于本地插件源，可以使用更简便的命令：

```bash
oedp repo make-local [path]
```

- `path`(可选)表示插件目录路径，默认为当前目录。命令会自动转换为绝对路径。

此命令等价于 `oedp repo make path file://path path`，适用于本地插件源的快速构建。

例如，在 `/opt/oedp/plugins` 目录下生成本地插件源索引：

```bash
cd /opt/oedp/plugins
oedp repo make-local
```

或者：

```bash
oedp repo make-local /opt/oedp/plugins
```
