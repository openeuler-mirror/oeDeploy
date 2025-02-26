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

from prettytable import PrettyTable

from src.exceptions.config_exception import ConfigException
from src.utils.log.logger_generator import LoggerGenerator
from src.utils.main_reader import MainReader


class InfoCmd:
    def __init__(self, project: str):
        """
        查看一个项目的详细信息。

        :param project: 项目目录路径
        """
        self.project = project
        self.log = LoggerGenerator().get_logger('info_cmd')

    def run(self):
        """
        查看一个项目的详细信息。

        :return: 是否执行成功
        """
        self.log.debug(f'Running cmd info: project={self.project}')  # 将日志等级调整为debug
        try:
            main = MainReader(self.project)
            name = main.get_name()
            version = main.get_version()
            description = main.get_description()
            action = main.get_action()
        except ConfigException as e:
            self.log.error(f'Failed to get project main info: {e}')
            return False
        action_list = []
        for action_name, detail in action.items():
            action_description = detail.get('description', '')
            action_list.append([len(action_list) + 1, action_name, action_description])

        headers = ['#', 'Action', 'Description']
        table = PrettyTable(headers)
        table.add_rows(action_list)

        self.log.info(f'name: {name}\n'
                      f'version: {version}\n'
                      f'description: {description}\n'
                      f'action:\n{table.get_string()}')
        return True
