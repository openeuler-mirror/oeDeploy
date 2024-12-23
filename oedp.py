#!/usr/bin/env python3
# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
# ======================================================================================================================

import sys

if f'/var/oedp/python/venv/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages' not in sys.path:
    sys.path.insert(
        0,
        f'/var/oedp/python/venv/oedp/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages'
    )
    sys.executable = '/var/oedp/python/venv/oedp/bin/python'

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
