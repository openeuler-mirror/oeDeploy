#!/bin/bash
current_path=$(cd $(dirname $0/); pwd)
source $current_path/lib/config.cfg

cp_into_container() {
    docker cp $current_path/lib $CONTAINER_NAME:/workspace
}

main() {
    set -e
    chmod -R +x $current_path/lib

    # 检测需要部署的节点ip数量
    if [ $NODE_NUM -ne 2 ]; then
        echo "当前仅支持两节点部署,当前数量是$NODE_NUM"
        exit 1
    fi

    # 1. 启动Docker容器并复制文件
    $current_path/lib/start_docker.sh
    cp_into_container

    # 2. 执行组网检查
    $current_path/lib/net_check.sh

    #进入容器执行
    # 3. 设置容器内环境变量
    docker exec -it $CONTAINER_NAME /workspace/lib/set_env.sh
    
}

# 执行主函数
main "$@"
