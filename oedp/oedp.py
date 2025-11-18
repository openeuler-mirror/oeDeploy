#!/usr/bin/env python3
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

import sys

# 尝试导入，如果失败则添加路径后重试
try:
    from src.constants.const import FAILED, OK
    from src.parsers.oedp_parser import OeDeployParser
except ModuleNotFoundError:
    # 如果导入失败，添加标准安装路径
    lib_dir = '/usr/lib/oedp'
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)
    # 重新导入
    from src.constants.const import FAILED, OK
    from src.parsers.oedp_parser import OeDeployParser

if __name__ == '__main__':
    try:
        ret = OeDeployParser().execute()
    except KeyboardInterrupt:
        print('Interrupted by user')
        exit(FAILED)
    if not ret:
        exit(FAILED)
    exit(OK)
