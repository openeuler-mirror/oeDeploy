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

from utils.logger import init_log

task_logger = init_log("taskmanager.log")


def generate_process_timeout_message(node):
    """
    进程超时退出时，生成错误信息，用于刷新数据库
    :param node
    :return:
    """
    return {}


def update_task_completed(message):
    """
    任务调度过程中，若所有节点都完成，更新Task表至完成状态
    :param message:
    :return:
    """
    pass


def schedule_model_service(message):
    """
    任务调度过程中更新对应数据库表
        Node、Step由views层进行初始化，任务调度过程中只做更新
        Report由任务调度进行初始化，并判断是否是重试的任务
    :param message:
    :return:
    """
    pass
