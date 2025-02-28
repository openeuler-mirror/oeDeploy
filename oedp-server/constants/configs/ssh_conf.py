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
# Create: 2025-02-13
# ======================================================================================================================

from configparser import MissingSectionHeaderError, ParsingError

from constants.paths import SSH_CONFIG_FILE
from utils.file_handler.base_handler import FileError
from utils.file_handler.conf_handler import ConfHandler
from utils.logger import init_log

__all__ = ['SSHConfig']

run_logger = init_log("run.log")

# 默认 SSH 建立连接的超时时间
DEFAULT_ESTABLISH_TIMEOUT = 120
# 默认命令提示符匹配超时时间
DEFAULT_EXPECT_PROMPTS_TIMEOUT = 120
# 默认 SSH 执行命令超时时间
DEFAULT_EXECUTE_CMD_TIMEOUT = 600
# 默认命令输出打印行数
DEFAULT_TAIL_SHOW_LINE_NUM = 100
# 默认命令行窗口高度
DEFAULT_WINDOW_HEIGHT = 24
# 默认命令行窗口余量宽度
DEFAULT_WINDOW_BUFFER_WIDTH = 150


class SSHConfig:
    # SSH 建立连接的超时时间
    ESTABLISH_TIMEOUT = DEFAULT_ESTABLISH_TIMEOUT
    # 命令提示符匹配超时时间
    EXPECT_PROMPTS_TIMEOUT = DEFAULT_EXPECT_PROMPTS_TIMEOUT
    # SSH 执行命令超时时间
    EXECUTE_CMD_TIMEOUT = DEFAULT_EXECUTE_CMD_TIMEOUT
    # tail 命令输出打印行数
    TAIL_SHOW_LINE_NUM = DEFAULT_TAIL_SHOW_LINE_NUM
    # 命令行窗口高度
    WINDOW_HEIGHT = DEFAULT_WINDOW_HEIGHT
    # 命令行窗口余量宽度，该宽度加上命令长度组成命令行窗口宽度
    WINDOW_BUFFER_WIDTH = DEFAULT_WINDOW_BUFFER_WIDTH


try:
    conf_handler = ConfHandler(file_path=SSH_CONFIG_FILE, logger=run_logger)
except (FileError, MissingSectionHeaderError, ParsingError):
    pass
else:
    try:
        SSHConfig.ESTABLISH_TIMEOUT = conf_handler.getint(
            'timeout', 'establish_timeout', default=DEFAULT_ESTABLISH_TIMEOUT)
    except ValueError:
        pass
    try:
        SSHConfig.EXPECT_PROMPTS_TIMEOUT = conf_handler.getint(
            'timeout', 'expect_prompts_timeout', default=DEFAULT_EXPECT_PROMPTS_TIMEOUT)
    except ValueError:
        pass
    try:
        SSHConfig.EXECUTE_CMD_TIMEOUT = conf_handler.getint(
            'timeout', 'execute_cmd_timeout', default=DEFAULT_EXECUTE_CMD_TIMEOUT)
    except ValueError:
        pass
    try:
        SSHConfig.TAIL_SHOW_LINE_NUM = conf_handler.getint(
            'size', 'tail_show_line_num', default=DEFAULT_TAIL_SHOW_LINE_NUM)
    except ValueError:
        pass
    try:
        SSHConfig.WINDOW_HEIGHT = conf_handler.getint('size', 'window_height', default=DEFAULT_WINDOW_HEIGHT)
    except ValueError:
        pass
    try:
        SSHConfig.WINDOW_BUFFER_WIDTH = conf_handler.getint(
            'size', 'window_buffer_width', default=DEFAULT_WINDOW_BUFFER_WIDTH)
    except ValueError:
        pass
