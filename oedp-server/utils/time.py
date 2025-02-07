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
# Create: 2025-02-05
# ======================================================================================================================

import pytz

from utils.cmd_executor import CommandExecutor


def get_time_zone():
    """
    获取系统时区
    :return: 返回系统时区，若未获取到系统时区则默认返回 Asia/Shanghai
    """
    default_time_zone = 'Asia/Shanghai'
    cmd = ['ls', '-l', '/etc/localtime']
    stdout, stderr, return_code = CommandExecutor(cmd).run()

    # 如果 return_code 为非 0，则命令执行失败
    if return_code:
        return default_time_zone

    contents = stdout.split('zoneinfo/')
    # 如果分割后的结果有两部分，说明成功获取时区信息
    if len(contents) == 2:
        time_zone = contents[-1].strip()
        # 校验获取的时区是否合法
        try:
            pytz.timezone(time_zone)
        except pytz.UnknownTimeZoneError:
            return default_time_zone  # 如果非法，返回默认时区
        return time_zone  # 如果合法，返回获取的时区
    return default_time_zone
