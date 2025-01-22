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
# Create: 2025-01-15
# ======================================================================================================================


# 判断是否静默安装
if [ -z "$1" ]; then
    is_silent_installation="false"
else
    if [[ "$1" == "-s" ]]; then
        is_silent_installation="true"
    else
        echo -e "\e[1;31mParameter [$1] is invalid, please use the '-s' parameter to indicate silent installation.\e[0m"
    fi
fi

SERVICE_DIR=$(realpath $(dirname $0))


# 配置 mariadb
source "${SERVICE_DIR}"/init_service.sh ${is_silent_installation}

# 根据用户输入修改ssh连接是否需要匹配公钥
source "${SERVICE_DIR}"/set_ssh_host_key_check_config.sh ${is_silent_installation}
