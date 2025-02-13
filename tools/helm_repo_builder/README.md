# Helm 镜像仓库搭建工具

## 1. 功能介绍

本工具旨在快速搭建 Helm 镜像仓库，提高 Helm 安装组件时的下载速度和稳定性，优化 Helm 使用体验。

## 2. 使用说明

使用以下命令以一键制作镜像仓库：

```shell
./helm-repo-builder.py <repo-url> [options]
python3 helm-repo-builder.py <repo-url> [options]
```

参数说明：

+ `repo-url`: 源仓库的 url，与`helm repo add`时使用的 url 相同。

可选参数：

+ `--url URL`: 指定镜像仓库的基础 url。
  + default: 空。**注意**：这将导致生成的`index.yaml`不含`urls`字段，采用相对路径检索`.tgz`文件。
+ `--path PATH`: 指定一个本地路径为下载根路径，用于存储 helm chart。
  + default: 当前路径。
+ `--prefix PREFIX`: 指定一个公共前缀，工具将对源下载地址剥离此前缀，然后以剩余的后缀构建目录树。
  + default: 自动分析公共前缀。
+ `--re-download`: 强制重新下载所有文件。
  + default: 不启用此选项。当本地存在对应文件且校验码正确时跳过。
+ `--no-index`: 只下载`.tgz`文件，不生成`index.yaml`文件。
  + default: 不启用此选项。
+ `--only-index`: 不下载`.tgz`文件，根据现有目录结构生成`index.yaml`文件。
  + default: 不启用此选项。
+ `--new-index`: 生成`index.yaml`文件时强制覆盖原`index.yaml`文件。
  + default: 不启用此选项。生成的`index.yaml`将在原文件上合并记录。
+ `--retry N`: 指定下载失败时的重试次数。
  + default: 5。