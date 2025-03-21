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

import time

from src.commands.run.run_action import RunAction
from src.exceptions.config_exception import ConfigException
from src.utils.log.logger_generator import LoggerGenerator
from src.utils.main_reader import MainReader
from decimal import Decimal


class RunCmd:
    def __init__(self, action: str, project: str, debug: bool):
        """
        执行一个项目中的方法。

        :param action: 方法名称
        :param project: 项目目录路径
        :param debug: 是否启用调试模式
        """
        self.action = action
        self.project = project
        self.debug = debug
        self.log = LoggerGenerator().get_logger('run_cmd')

    def run(self):
        """
        执行一个项目中的方法。

        :return: 是否执行成功
        """
        start_time = time.time()
        self.log.info(f'Start time: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))}')
        try:
            self.log.debug(f'Running cmd run: action={self.action}, project={self.project}')
            try:
                main = MainReader(self.project)
                action = main.get_action_detail(self.action)
            except ConfigException as e:
                self.log.error(f'Failed to get project main info: {e}')
                return False
            if 'tasks' not in action:
                self.log.error(f'Failed to get tasks info: {action}')
                return False
            tasks = action['tasks']
            return RunAction(self.action, tasks, self.project, self.debug).run()
        finally:
            end_time = time.time()
            seconds = Decimal(f"{format(end_time - start_time, '.1f')}")
            formatted_time = time.strftime("%H:%M:%S", time.gmtime(float(seconds)))
            elapsed_time = f"{formatted_time}.{int((seconds % 1) * 10)}"
            self.log.info(f'End time: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))}')
            self.log.info(f'Elapsed time: {elapsed_time}')
