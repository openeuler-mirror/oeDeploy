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
# Create: 2025-01-15
# ======================================================================================================================

from configparser import MissingSectionHeaderError, ParsingError

from constants.paths import TASK_CONFIG_FILE
from utils.file_handler.base_handler import FileError
from utils.file_handler.conf_handler import ConfHandler
from utils.logger import init_log

__all__ = ['TaskConfig']

run_logger = init_log("run.log")

DEFAULT_MAX_TASK_NUMBER = 1000
DEFAULT_MAX_REPO_NUMBER = 50
DEFAULT_MAX_USER_TASK_NUMBER = 50
DEFAULT_MAX_TASK_NODE = 1000
DEFAULT_THREAD_TIMEOUT = 30


class TaskConfig:
    MAX_TASK_NUMBER = DEFAULT_MAX_TASK_NUMBER
    MAX_REPO_NUMBER = DEFAULT_MAX_REPO_NUMBER
    MAX_USER_TASK_NUMBER = DEFAULT_MAX_USER_TASK_NUMBER
    MAX_TASK_NODE = DEFAULT_MAX_TASK_NODE
    THREAD_TIMEOUT = DEFAULT_THREAD_TIMEOUT


try:
    conf_handler = ConfHandler(file_path=TASK_CONFIG_FILE, logger=run_logger)
except (FileError, MissingSectionHeaderError, ParsingError):
    pass
else:
    try:
        TaskConfig.MAX_TASK_NUMBER = conf_handler.getint(
            'scheduler', 'max_task_number', default=DEFAULT_MAX_TASK_NUMBER)
    except ValueError:
        pass
    try:
        TaskConfig.MAX_REPO_NUMBER = conf_handler.getint(
            'scheduler', 'max_repo_number', default=DEFAULT_MAX_REPO_NUMBER)
    except ValueError:
        pass
        TaskConfig.MAX_USER_TASK_NUMBER = conf_handler.getint(
            'scheduler', 'max_user_task_number', default=DEFAULT_MAX_USER_TASK_NUMBER)
    try:
        TaskConfig.MAX_TASK_NODE = conf_handler.getint('scheduler', 'max_task_node', default=DEFAULT_MAX_TASK_NODE)
    except ValueError:
        pass
    try:
        TaskConfig.THREAD_TIMEOUT = conf_handler.getint('scheduler', 'thread_timeout', default=DEFAULT_THREAD_TIMEOUT)
    except ValueError:
        pass
