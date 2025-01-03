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

from tabulate import tabulate

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
        self.log.info(f'Running cmd info: project={self.project}')
        try:
            main = MainReader(self.project)
            name = main.get_name()
            version = main.get_version()
            description = main.get_description()
            action = main.get_action()
        except ConfigException as e:
            self.log.error(f'Failed to get project main info: {e}')
            print('Failed to show project info.')
            return False
        action_list = []
        for action_name, detail in action.items():
            description = detail.get('description', '')
            action_list.append([len(action_list) + 1, action_name, description])

        print(f'name: {name}')
        print(f'version: {version}')
        print(f'description: {description}')
        print(f'action:')
        headers = ['#', 'Action', 'Description']
        print(tabulate(action_list, headers=headers, tablefmt='grid'))
        return True
