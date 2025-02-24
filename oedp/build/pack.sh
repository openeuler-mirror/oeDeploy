#!/usr/bin/env bash
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2025-02-21
# ======================================================================================================================

set -ex

source $(dirname $0)/constants.sh

# 创建打包目录并复制文件
echo -e "\e[1;32m [INFO] Start to prepare packing directory \e[0m"
[ -d "${PACKING_DIR}" ] && rm -rf "${PACKING_DIR}"
mkdir -p "${PACKING_DIR}"
cd "${PROJECT_DIR}"
cp -R src oedp.py build/static "${PACKING_DIR}"
echo -e "\e[1;32m [INFO] The packing directory si ready \e[0m"

echo -e "\e[1;32m [INFO] Start to convert a newline character \e[0m"
find "${PACKING_DIR}" -type f -name "*.py" -o -name "*.sh" | xargs dos2unix
dos2unix "${BUILD_SCRIPT_DIR}"/oedp.spec
echo -e "\e[1;32m [INFO] Convert a newline character successfully \e[0m"

echo -e "\e[1;32m [INFO] Start to pack source code \e[0m"
cd "${TEMP_DIR}"
[ -f "${PACKING_DIR_NAME}.tar.gz" ] && rm -f "${PACKING_DIR_NAME}.tar.gz"
tar czf "${PACKING_DIR_NAME}.tar.gz" "${PACKING_DIR_NAME}"
echo -e "\e[1;32m [INFO] Source code packed successfully \e[0m"