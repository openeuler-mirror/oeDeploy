# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
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
