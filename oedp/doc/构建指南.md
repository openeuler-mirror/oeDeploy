# 构建指南

## 1.环境准备

准备两台 openEuler 24.03 的机器，x86_64 和 aarch64 各一台，需要可以访问外部网络。在环境上需要安装如下构建依赖：

```
yum install -y automake bzip2 bzip2-devel bzip2-libs cmake dos2unix expat expat-devel gcc gcc-c++ glibc-devel \
glibc-static libffi-devel make openssl openssl-devel pcre-devel rpm-build rpm-devel rpmdevtools tcl unzip zlib-devel python3
```

## 2. 准备构建工作目录

(1) 创建目录 `build_workspace`。

(2) 放置 oeDeploy 仓库到目录 `build_workspace` 下。

## 3. 执行构建脚本

进入构建工作目录 `build_workspace`,执行如下脚本，命令如下：

```
cd build_workspace
sh oeDeploy/oedp/build/pack.sh
sh oeDeploy/oedp/build/build.sh
```

构建脚本执行成功后，构建好的 RPM 包在目录 `build_workspace/storages` 下。