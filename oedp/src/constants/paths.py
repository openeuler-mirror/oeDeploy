# -*- coding: utf-8 -*-
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

"""
记录路径常量
"""

from os.path import join

"""
project
|-- main.yaml
|-- config.yaml
`-- workspace
    `-- ...
"""
PROJECT_MAIN = 'main.yaml'
PROJECT_CONFIG = 'config.yaml'
PROJECT_WORKSPACE_DIR = 'workspace'

"""
/var
`-- oedp
    |-- plugin
    |   |-- k8s
    |   `-- kubeflow
    `-- log
        `-- xxx.log
"""
# oedp 除配置外的家目录
OEDP_HOME = "/var/oedp"
# 插件缓存目录
PLUGIN_DIR = join(OEDP_HOME, 'plugin')
# 日志文件所在目录
LOG_DIR = join(OEDP_HOME, "log")

# oedp 配置家目录
OEDP_CONFIG_HOME_DIR = "/etc/oedp"
# 配置文件目录
OEDP_CONFIG_DIR = join(OEDP_CONFIG_HOME_DIR, "config")
# 日志配置文件所在目录
LOG_CONFIG_DIR = join(OEDP_CONFIG_DIR, "log")
