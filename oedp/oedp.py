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

if '/usr/lib/oedp' not in sys.path:
    sys.path.append('/usr/lib/oedp')
    sys.executable = '/usr/bin/python3'

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
