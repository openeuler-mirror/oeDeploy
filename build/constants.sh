#!/usr/bin/env bash
# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
# ======================================================================================================================

set -e

# 工作空间目录
WORKSPACE_DIR=$(pwd)

# 备份目录
BACKUP_DIR="${WORKSPACE_DIR}"/backup
# Python 第三方库目录
PYTHON_THIRD_LIBS_DIR=${BACKUP_DIR}/python_third_libs

# RPM 归档地址
STORAGE_DIR="${WORKSPACE_DIR}"/storages

# 项目仓库目录
PROJECT_DIR="${WORKSPACE_DIR}"/oeDeploy
# 构建脚本所在目录
BUILD_SCRIPT_DIR="${PROJECT_DIR}"/build
# 存放构建中间产物的暂存目录
TEMP_DIR="${PROJECT_DIR}"/temp
# 打包目录
PACKING_DIR_NAME=oedp-1.0.0
PACKING_DIR="${TEMP_DIR}/${PACKING_DIR_NAME}"

# 系统架构
if [[ "$(arch)" == "x86_64" ]]; then
    ARCH="x86"
elif [[ "$(arch)" == "aarch64" ]]; then
    ARCH="arm"
fi
# 构建环境 CPU 核心数
CPU_COUNT=$(grep -c processor /proc/cpuinfo)
# pip 源 URL
PIP_SOURCE_URL='https://mirrors.aliyun.com/pypi/simple/'