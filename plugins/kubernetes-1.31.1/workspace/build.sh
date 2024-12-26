#!/bin/bash
# SPDX-License-Identifier: MulanPSL-2.0+
# Copyright (c) 2020 Huawei Technologies Co., Ltd. All rights reserved.

set -e

KUBERNETES_VERSION=${KUBERNETES_VERSION:-"1.31.1"}
CONTAINERD_VERSION=${CONTAINERD_VERSION:-"1.7.22"}
CALICO_VERSION=${CALICO_VERSION:-"3.28.2"}

DOCKER_PROXY=${DOCKER_PROXY:-"m.daocloud.io/"}
# 官方地址：https://dl.k8s.io mirror参考: https://github.com/DaoCloud/public-binary-files-mirror
DL_K8S_IO_URL=${DL_K8S_IO_URL:-"https://files.m.daocloud.io/dl.k8s.io"}
# github代理：https://gh-proxy.test.osinfra.cn//  https://gh.idayer.com/  
GITHUB_PROXY=${GITHUB_PROXY:-"https://gh-proxy.test.osinfra.cn/"}

CURRENT_PATH=$(cd `dirname $0/`;pwd)

HOST_ARCH=$(uname -m)
case "$HOST_ARCH" in
    x86_64)
        HOST_ARCH="amd64"
        SUPPORTED_ARCH=( "amd64" "arm64" )
        ;;
    aarch64)
        HOST_ARCH="arm64"
        SUPPORTED_ARCH=( "arm64" "amd64" )
        ;;
esac

_download_and_save_image() {
    local image=$1
    local path=$2
    local arch=$3
    if [[ -n "$DOCKER_PROXY" ]]; then
        docker pull --platform linux/$arch $DOCKER_PROXY$image
        docker tag $DOCKER_PROXY$image $image
    else
        docker pull --platform linux/$arch $image
    fi

    tar_name=`echo "$image" | awk -F'/' '{print $NF}' | awk -F':' '{print $1}'`
    docker save -o "$path/$tar_name".tar $image
}

prepare_kubernetes_binaries() {
    local arch=$1

    local tmp_dir="$CURRENT_PATH/tmp/$arch"
    local ctd_dir="$CURRENT_PATH/roles/prepare/containerd/files/$arch"
    local k8s_dir="$CURRENT_PATH/roles/prepare/kubernetes/files/$arch"

    mkdir -p $tmp_dir
    mkdir -p $ctd_dir
    mkdir -p $k8s_dir

    pushd $tmp_dir

    local containerd_pkg="containerd-$CONTAINERD_VERSION-linux-$arch.tar.gz"
    [ ! -e $containerd_pkg ] && wget --no-check-certificate "$GITHUB_PROXY"https://github.com/containerd/containerd/releases/download/v$CONTAINERD_VERSION/$containerd_pkg
    tar xzvf $containerd_pkg && echo "Extracted $containerd_pkg successfully" || { rm -f $containerd_pkg; echo "Download containerd failed"; exit 1; }
    cp $tmp_dir/bin/* $ctd_dir
    
    [ ! -e runc.$arch ] && wget --no-check-certificate "$GITHUB_PROXY"https://github.com/opencontainers/runc/releases/download/v1.1.15/runc.$arch
    cp runc.$arch $ctd_dir/runc

    local crictl_pkg="crictl-v1.31.1-linux-$arch.tar.gz"
    [ ! -e $crictl_pkg ] && wget --no-check-certificate "$GITHUB_PROXY"https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.31.1/$crictl_pkg
    tar Cxzvf $k8s_dir/ $crictl_pkg && echo "Extracted $crictl_pkg successfully" || { rm -f $crictl_pkg; echo "Download crictl failed"; exit 1; }

    local kubernetes_download_url="$DL_K8S_IO_URL/v$KUBERNETES_VERSION/bin/linux/$arch"
    components=(
        "kubeadm"
        "kubelet"
        "kubectl"
    )
    for component in "${components[@]}"; do
        [ ! -e "$component.$KUBERNETES_VERSION" ] && wget --no-check-certificate "$kubernetes_download_url/$component" -O "$component.$KUBERNETES_VERSION"
        cp "$component.$KUBERNETES_VERSION" "$k8s_dir/$component"
    done

    popd
}

prepare_kubernetes_images() {
    local dest_dir="$CURRENT_PATH/roles/prepare/images/files/$arch"
    mkdir -p $dest_dir

    if [ ${#KUBERNETES_IMAGES[@]} -eq 0 ]; then
        chmod +x "roles/prepare/kubernetes/files/$HOST_ARCH/kubeadm"
        export KUBERNETES_IMAGES=(`"./roles/prepare/kubernetes/files/$HOST_ARCH/kubeadm" config images list --kubernetes-version=$KUBERNETES_VERSION`) 
    fi

    for image in "${KUBERNETES_IMAGES[@]}"; do
        _download_and_save_image $image $dest_dir $arch
        if [ -z $PAUSE_IMAGE ]; then
            [[ "$image" == *"pause"* ]] && export PAUSE_IMAGE=$image
        fi
    done    
}

prepare_plugins_calico() {
    local arch=$1
    local dest_dir="roles/plugins/calico/files/$arch"
    mkdir -p $dest_dir

    if [ ${#CALICO_IMAGES[@]} -eq 0 ]; then
        if [ ! -e tmp/calico-v$CALICO_VERSION.yaml ]; then
            wget --no-check-certificate "$GITHUB_PROXY"https://raw.githubusercontent.com/projectcalico/calico/v$CALICO_VERSION/manifests/calico.yaml -O tmp/calico-v$CALICO_VERSION.yaml
            cp tmp/calico-v$CALICO_VERSION.yaml roles/plugins/calico/files/calico-v$CALICO_VERSION.yaml
        fi

        export CALICO_IMAGES=(`grep "image:" tmp/calico-v$CALICO_VERSION.yaml | uniq | awk '{print $2}'`)

        if [ ${#CALICO_IMAGES[@]} -eq 0 ]; then
            rm -f tmp/calico-v$CALICO_VERSION.yaml
            echo "Download calico-v$CALICO_VERSION.yaml failed. Try to run build.sh again..."
            exit 1
        fi
    fi

    for image in "${CALICO_IMAGES[@]}"; do
        _download_and_save_image $image $dest_dir $arch
    done

}

pushd $CURRENT_PATH

declare -a KUBERNETES_IMAGES=()
declare -a CALICO_IMAGES=()

for arch in "${SUPPORTED_ARCH[@]}"; do
    prepare_kubernetes_binaries $arch
    prepare_kubernetes_images $arch
    prepare_plugins_calico $arch
done

sed -i "s/^kubernetes_version:/kubernetes_version: $KUBERNETES_VERSION/"
sed -i "s/^pause_image:/pause_image: $PAUSE_IMAGE/"
sed -i "s/^calico_version:/calico_version: $CALICO_VERSION/"

# needed: ansible roles init-k8s.yml delete-k8s.yml clean-k8s.yml variables.yml build.sh

popd