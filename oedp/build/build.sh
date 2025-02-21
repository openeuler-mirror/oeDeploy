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

set -ex

source $(dirname $0)/constants.sh
if [ ! -z $1 ]; then
    [ ! -d "$(dirname $1)" ] && mkdir "$(dirname $1)"
    exec >> "$1" 2>&1
fi

echo -e "\e[1;32m [INFO] Start to build RPM \e[0m"
[ -d ~/rpmbuild ] && rm -rf ~/rpmbuild
rpmdev-setuptree
cp "${BUILD_SCRIPT_DIR}"/oedp.spec ~/rpmbuild/SPECS/
cp "${TEMP_DIR}/${PACKING_DIR_NAME}.tar.gz" ~/rpmbuild/SOURCES/
sed -i "s/release_number/$(date +'%Y%m%d')/g" ~/rpmbuild/SPECS/oedp.spec
sed -i '/case / s/^\(.*\)$/#\1/g' ~/.rpmmacros
# 在构建 RPM 包时，禁用编译 pyc
second_line=$(sed -n '2{s/^[[:space:]]*//;s/[[:space:]]*$//;p}' /usr/lib/rpm/brp-python-bytecompile)
[ "$second_line" != "exit 0" ] && sudo sed -i '1 a exit 0' /usr/lib/rpm/brp-python-bytecompile
rpmbuild -bb ~/rpmbuild/SPECS/oedp.spec
echo -e "\e[1;32m [INFO] oedp built successfully \e[0m"

echo -e "\e[1;32m [INFO] Start to store RPMs \e[0m"
cd "${WORKSPACE_DIR}"
[ ! -d "${STORAGE_DIR}" ] && mkdir "${STORAGE_DIR}"
sub_dir=$(date +'%Y%m%d%H%M')
mkdir "${STORAGE_DIR}/${sub_dir}"
cp -f ~/rpmbuild/RPMS/$(arch)/*.rpm "${STORAGE_DIR}/${sub_dir}"
rpm_name=$(ls ~/rpmbuild/RPMS/$(arch))
echo -e "\e[1;32m [INFO] RPM is stored in ${STORAGE_DIR}/${sub_dir}/${rpm_name} \e[0m"

echo -e "\e[1;32m [INFO] Start to clean up environment \e[0m"
[ -d "${PACKING_DIR}" ] && rm -rf "${PACKING_DIR}"
echo -e "\e[1;32m [INFO] Clean up environment successfully \e[0m"