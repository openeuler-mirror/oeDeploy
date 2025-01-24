#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2025-01-14
# ======================================================================================================================

import os

# oedp-server 工作目录
OEDP_SERVER_WORK_DIR = '/var/oedp-server'
# oedp-server 日志目录
LOG_DIR = os.path.join(OEDP_SERVER_WORK_DIR, 'log')
# 第三方软件目录
THIRDAPP_INSTALL_DIR = os.path.join(OEDP_SERVER_WORK_DIR, 'thirdapps')
# OpenSSL 目录
OPENSSL_DIR = os.path.join(THIRDAPP_INSTALL_DIR, 'openssl')
# libcrypto.so 文件路径
LIBCRYPTO_SO_FILE = os.path.join(OPENSSL_DIR, 'libcrypto.so')

# oedp-server 配置文件路径
OEDP_SERVER_CONFIG_DIR = '/etc/oedp-server'
# task.conf 配置文件路径
TASK_CONFIG_FILE = os.path.join(OEDP_SERVER_CONFIG_DIR, 'task.conf')
# mariadb.conf 配置文件路径
MARIADB_CONFIG_FILE = os.path.join(OEDP_SERVER_CONFIG_DIR, 'mariadb', 'mariadb.conf')
# 密钥文件路径
SECRET_KEY_FILE = os.path.join(OEDP_SERVER_CONFIG_DIR, 'mariadb', 'mariadb.json')
