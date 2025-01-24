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

from enum import Enum

from constants.paths import TASK_CONFIG_FILE
from utils.config_parser import ConfParser
from utils.logger import init_log

task_logger = init_log("taskmanager.log")
config_parser = ConfParser(task_logger, TASK_CONFIG_FILE)

__all__ = ['TaskConfig']


class TaskConfig(Enum):
    MAX_TASK_NUMBER = config_parser.get('scheduler', 'max_task_number', default=1000)
    MAX_REPO_NUMBER = config_parser.get('scheduler', 'max_repo_number', default=50)
    MAX_USER_TASK_NUMBER = config_parser.get('scheduler', 'max_user_task_number', default=50)
    MAX_TASK_NODE = config_parser.get('scheduler', 'max_task_node', default=1000)
    THREAD_TIMEOUT = config_parser.get('scheduler', 'thread_timeout', default=30)
