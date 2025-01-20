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

from abc import ABC, abstractmethod
from copy import deepcopy
from multiprocessing import Queue
from typing import NoReturn, Dict


class TaskStatus:
    """
    记录各任务的状态
    """
    SUCCESS = 0
    FAILED = 1
    RUNNING = 2

    @staticmethod
    def task_is_completed(status):
        """
        任务是否完成
        :param status:
        :return:
        """
        return status in (TaskStatus.SUCCESS, TaskStatus.FAILED)


class BaseTask(ABC):
    """
    定义任务类的基类，每个节点为一个独立的任务
    """

    def __init__(self, node: Dict):
        self.node = node  # node保存节点基本信息，用于调度进程与子进程通信及调度进程对数据库状态的更新
        self.return_message = {
            "id": "",
            "current_step": "",
            "current_step_status": "",
            "current_step_status_progress": 0,
            "current_step_message": "",
            "is_completed": ""
        }

    @abstractmethod
    def start(self, *args, **kwargs):
        """
        作为各个任务的入口函数，子类必须实现
        :return:
        """
        pass

    @abstractmethod
    def clear(self, *args, **kwargs):
        """
        作为各个任务的失败清理函数，子类必须实现
        :return:
        """
        pass

    def _update_return_message(self, message_queue: Queue, **kwargs) -> NoReturn:
        step_status = kwargs.get("step_status")

        if step_status:
            self.return_message["step_status"] = step_status

        message_queue.put(deepcopy(self.return_message))
