# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2025-01-21
# ======================================================================================================================

# 根据用户输入修改ssh连接是否需要匹配公钥

is_silent_installation=$1
SSH_CONFIG_FILE="/etc/ssh/ssh_config"

# 获取用户输入
    while true
    do
        echo -e "\e[1;40;34mIf authentication is enabled,\e[0m"
        echo -e "\e[1;40;34mthe SSH connection fails after the fingerprint of the machine changes.\e[0m"
        echo -n -e "\e[1;40;34mPlease confirm whether public key authentication is not required for SSH connection(y/n default: n):\e[0m"
        if [ "${is_silent_installation}" == "false" ]; then
            read -r answer
        else
            answer="n"
        fi
        if [ -z "${answer}" ]
        then
            answer="n"
            break;
        elif [ "${answer}" == "n" ] || [ "${answer}" == "y" ]
        then
            break;
        else
          echo -e "\e[1;31mPlease input 'y' or 'n'\e[0m"
        fi
    done
    # 根据用户输入对ssh配置文件做修改
    if [ ! -w "${SSH_CONFIG_FILE}" ];then
       echo -e "\e[1;31m${SSH_CONFIG_FILE} can not write, modify fail.\e[0m"
       return
    fi
    if [ "${answer}" == "y" ];then
        sed -i 's/^StrictHostKeyChecking.*//' ${SSH_CONFIG_FILE}
        sed -i 's/^\s*StrictHostKeyChecking.*//' ${SSH_CONFIG_FILE}
        sed -i 's/^UserKnownHostsFile.*//' ${SSH_CONFIG_FILE}
        sed -i 's/^\s*UserKnownHostsFile.*//' ${SSH_CONFIG_FILE}
        sed -i '$a StrictHostKeyChecking no' ${SSH_CONFIG_FILE}
        sed -i '$a UserKnownHostsFile=\/dev\/null' ${SSH_CONFIG_FILE}
    fi
