#!/usr/bin/env bash
# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
# ======================================================================================================================

set -ex

source $(dirname $0)/constants.sh
if [ ! -z $1 ]; then
    [ ! -d "$(dirname $1)" ] && mkdir "$(dirname $1)"
    exec >> "$1" 2>&1
fi

function prepare_packing_dir() {
    # 创建打包目录并复制文件
    echo -e "\e[1;32m [INFO] Start to prepare packing directory \e[0m"
    cd "${PROJECT_DIR}"
    [ -d "${PACKING_DIR}" ] && rm -rf "${PACKING_DIR}"
    mkdir "${PACKING_DIR}"
    cp -R src oedp.py build/static "${PYTHON_THIRD_LIBS_DIR}" "${PACKING_DIR}"
    echo -e "\e[1;32m [INFO] The packing directory si ready \e[0m"
}

function dos_2_unix() {
    echo -e "\e[1;32m [INFO] Start to convert a newline character \e[0m"
    find "${PACKING_DIR}" -type f -name "*.py" -o -name "*.sh" | xargs dos2unix
    dos2unix "${BUILD_SCRIPT_DIR}"/oedp.spec
    echo -e "\e[1;32m [INFO] Convert a newline character successfully \e[0m"
}

function pack_dir() {
    echo -e "\e[1;32m [INFO] Start to pack source code \e[0m"
    cd "${TEMP_DIR}"
    [ -f "${PACKING_DIR_NAME}.tar.gz" ] && rm -f "${PACKING_DIR_NAME}.tar.gz"
    tar czf "${PACKING_DIR_NAME}.tar.gz" "${PACKING_DIR_NAME}"
    echo -e "\e[1;32m [INFO] Source code packed successfully \e[0m"
}

function build_rpm() {
    echo -e "\e[1;32m [INFO] Start to build RPM \e[0m"
    [ -d ~/rpmbuild ] && rm -rf ~/rpmbuild
    rpmdev-setuptree
    cp "${BUILD_SCRIPT_DIR}"/oedp.spec ~/rpmbuild/SPECS/
    cp "${TEMP_DIR}/${PACKING_DIR_NAME}.tar.gz" ~/rpmbuild/SOURCES/
    sed -i "s/release_number/$(date +'%Y%m%d')/g" ~/rpmbuild/SPECS/oedp.spec
    sed -i '/case / s/^\(.*\)$/#\1/g' ~/.rpmmacros
    # 在构建 RPM 包时，禁用编译 pyc
    sudo sed -i '1 a exit 0' /usr/lib/rpm/brp-python-bytecompile
    sudo sed -i '1 a exit 0' /usr/lib/rpm/check-buildroot
    sudo sed -i '1 a exit 0' /usr/lib/rpm/check-rpaths
    rpmbuild -bb ~/rpmbuild/SPECS/oedp.spec
    echo -e "\e[1;32m [INFO] oedp built successfully \e[0m"
}

function archive_rpm() {
    echo -e "\e[1;32m [INFO] Start to store RPMs \e[0m"
    cd "${WORKSPACE_DIR}"
    [ ! -d "${STORAGE_DIR}" ] && mkdir "${STORAGE_DIR}"
    sub_dir=$(date +'%Y%m%d%H%M')
    mkdir "${STORAGE_DIR}/${sub_dir}"
    cp -f ~/rpmbuild/RPMS/$(arch)/*.rpm "${STORAGE_DIR}/${sub_dir}"
    rpm_name=$(ls ~/rpmbuild/RPMS/$(arch))
    echo -e "\e[1;32m [INFO] RPM is stored in ${STORAGE_DIR}/${sub_dir}/${rpm_name} \e[0m"
}

function clean_env() {
    echo -e "\e[1;32m [INFO] Start to clean up environment \e[0m"
    [ -d "${PACKING_DIR}" ] && rm -rf "${PACKING_DIR}"
    echo -e "\e[1;32m [INFO] Clean up environment successfully \e[0m"
}

function main() {
    # 检查暂存目录
    if [ ! -d "${TEMP_DIR}" ]; then
        mkdir "${TEMP_DIR}"
        echo -e "\e[1;32m [INFO] Create a staging directory ${TEMP_DIR} \e[0m"
    fi

    # 创建打包目录
    prepare_packing_dir

    # 转换换行符
    dos_2_unix

    # 打压缩包
    pack_dir

    # 构建 RPM 包
    build_rpm

    # RPM 包归档
    archive_rpm

    # 环境清理
    clean_env
}

main