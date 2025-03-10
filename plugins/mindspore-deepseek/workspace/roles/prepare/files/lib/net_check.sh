#!/bin/bash

# 设置TLS
for i in {0..7}; do
    hccn_tool -i $i -tls -s enable 0
done

# 检查TLS状态
for i in {0..7}; do
    hccn_tool -i $i -tls -g | grep switch
done

# 检查链路状态
for i in {0..7}; do
    hccn_tool -i $i -link -g | grep -i 'link status: UP'
    if [ $? -ne 0 ]; then
        echo "节点npu设备 $i 检测link status不为UP"
        exit 1
    fi
done

# 检查网络健康状态
for i in {0..7}; do
    hccn_tool -i $i -net_health -g | grep -i 'Success'
    if [ $? -ne 0 ]; then
        echo "节点npu设备 $i 检测net_health不为Success"
    fi
done

# 检查IP信息
for i in {0..7}; do
    hccn_tool -i $i -ip -g
done

# 添加机器卡间互联检查
check_inter_device_connection() {
    echo -e "${BLUE}请输入目标NPU卡的IP地址 (输入q退出检查):${NC}"
    while true; do
        read -p "IP地址: " target_ip
        if [ "$target_ip" = "q" ]; then
            break
        fi
        
        if [[ ! $target_ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo -e "${RED}无效的IP地址格式，请重新输入${NC}"
            continue
        fi
        
        echo -e "\n${BLUE}正在检查与 $target_ip 的连接...${NC}"
        for i in {0..7}; do
            echo -e "\n本机设备 $i ping $target_ip:"
            hccn_tool -i $i -ping -g address $target_ip
        done
        
        echo -e "\n${BLUE}是否继续检查其他IP？(输入q退出，输入其他继续)${NC}"
        read -p "选择: " choice
        if [ "$choice" = "q" ]; then
            break
        fi
    done
}

main() {
    if [ "$1" = "--check-connection" ]; then
        check_inter_device_connection
    fi
}

main "$@"
