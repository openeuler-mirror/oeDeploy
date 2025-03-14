#!/bin/bash
current_path=$(
    cd $(dirname $0/)
    pwd
)
source $current_path/lib/config.cfg

cp_into_container() {
    docker cp $current_path/lib $CONTAINER_NAME:/workspace
}

main() {
    set -e
    chmod -R +x $current_path/lib

    systemctl stop firewalld
    systemctl stop iptables

    # 检查防火墙是否启动，如果启动则检查端口是否在防火墙白名单中，如果不存在则添加到白名单中
    status=$(systemctl status firewalld | grep -E "Active" | awk -F":" '{print $2}' | awk -F" " '{print $1}')
    if [[ "${status}" == "active" ]]; then
        # ray 端口防火墙检查
        port_ray=$(firewall-cmd --query-port=$RAY_PORT/tcp)
        if [[ "${port_ray}" == "no" ]]; then
            port_ray=$(firewall-cmd --zone=public --add-port=$RAY_PORT/tcp --permanent)
            firewall-cmd --reload
        fi
        port_ray=$(firewall-cmd --query-port=$RAY_PORT/tcp)
        if [[ "${port_ray}" != "yes" ]]; then
            echo -e "防火墙开启 $RAY_PORT端口失败"
            exit 1
        fi
        port_llm=$(firewall-cmd --query-port=$LLM_PORT/tcp)
        if [[ "${port_llm}" == "no" ]]; then
            port_llm=$(firewall-cmd --zone=public --add-port=$LLM_PORT/tcp --permanent)
            firewall-cmd --reload
        fi
        port_llm=$(firewall-cmd --query-port=$LLM_PORT/tcp)
        if [[ "${port_llm}" != "yes" ]]; then
            echo -e "防火墙开启 $LLM_PORT端口失败"
            exit 1
        fi
    fi

    # 检测需要部署的节点ip数量
    if [ [ $NODE_NUM -ne 2 ] && [ $NODE_NUM -ne 4 ] ]; then
        echo "当前仅支持两/四节点部署,当前数量是$NODE_NUM"
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
