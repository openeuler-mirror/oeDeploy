#!/bin/bash
current_path=$(
    cd $(dirname $0/)
    pwd
)
ENV_FILE=/root/.bashrc
source $current_path/config.cfg
source $ENV_FILE
ray_start() {
    ps -ef | grep "python" | grep -v grep | awk '{print $2}' | xargs kill
    ray stop

    if [ "$1" ]; then
        # 从节点
        nohup ray start --address=$1:$RAY_PORT &
    else
        # 主节点
        nohup ray start --head --include-dashboard=False --port=$RAY_PORT &
        sleep 5
        for i in {1..10}; do
            ray status | grep '8.0 NPU'
            if [ $? -eq 0 ]; then
                echo "主节点ray已启动"
                break
            fi
            sleep 3
        done
    fi
    echo "ray 已在后台运行"
}

ray_start "$@"
