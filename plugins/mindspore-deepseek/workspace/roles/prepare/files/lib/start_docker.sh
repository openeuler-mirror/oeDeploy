#!/bin/bash

# 各个节点均执行
current_path=$(
    cd $(dirname $0/)
    pwd
)
source $current_path/config.cfg
# 安装docker
yum install docker -y

# 检测镜像是否已被拉取
docker images | grep $IMAGE_NAME | grep $IMAGE_TAG
if [ $? -ne 0 ]; then
    docker pull $IMAGE_NAME:$IMAGE_TAG
    if [ $? -ne 0 ]; then
        echo "docker镜像拉取失败，请手动下载并加载"
        exit 1
    fi
fi

# 停止所有现存容器实例
if [ $IS_STOP_OTHER_CONTAINER -ne 0 ]; then
    docker stop $(docker ps -aq)
fi

# 如果存在名称相同的容器，则直接使用
docker ps -a | grep $IMAGE_NAME:$IMAGE_TAG | grep $CONTAINER_NAME
if [ $? -eq 0 ]; then
    echo "发现容器 $CONTAINER_NAME 已存在，直接使用"
    docker start $CONTAINER_NAME
    exit 0
fi

# 如果存在名称相同，但镜像不同容器，则报错
docker ps -a | grep $CONTAINER_NAME
if [ $? -eq 0 ]; then
    echo "发现容器名称 $CONTAINER_NAME 已被使用，请排查"
    exit 1
fi

# 拉起容器实例
docker run -itd --privileged --hostname $(hostname) --name=$CONTAINER_NAME --net=host \
    --shm-size 500g \
    --device=/dev/davinci0 \
    --device=/dev/davinci1 \
    --device=/dev/davinci2 \
    --device=/dev/davinci3 \
    --device=/dev/davinci4 \
    --device=/dev/davinci5 \
    --device=/dev/davinci6 \
    --device=/dev/davinci7 \
    --device=/dev/davinci_manager \
    --device=/dev/hisi_hdc \
    --device /dev/devmm_svm \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
    -v /usr/local/Ascend/firmware:/usr/local/Ascend/firmware \
    -v /usr/local/sbin/npu-smi:/usr/local/sbin/npu-smi \
    -v /usr/local/sbin:/usr/local/sbin \
    -v /usr/sbin:/usr/sbin \
    -v /etc/hccn.conf:/etc/hccn.conf \
    -v /usr/bin/netstat:/usr/bin/netstat \
    -v /usr/bin/lscpu:/usr/bin/lscpu \
    -v $MODEL_PATH:$MODEL_PATH \
    --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
    $IMAGE_NAME:$IMAGE_TAG \
    bash
