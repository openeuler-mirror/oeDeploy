#!/usr/bin/env bash
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2024-12-23
# ======================================================================================================================

set -e

# 工作空间目录
WORKSPACE_DIR=$(pwd)

# RPM 归档地址
STORAGE_DIR="${WORKSPACE_DIR}"/storages

# 项目仓库目录 - oedp 命令行相关代码所在目录
PROJECT_DIR="${WORKSPACE_DIR}"/oeDeploy/oedp
# 构建脚本所在目录
BUILD_SCRIPT_DIR="${PROJECT_DIR}"/build
# 存放构建中间产物的暂存目录
TEMP_DIR="${PROJECT_DIR}"/temp
# 打包目录
PACKING_DIR_NAME=oedp-1.0.0
PACKING_DIR="${TEMP_DIR}/${PACKING_DIR_NAME}"