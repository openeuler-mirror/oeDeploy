# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
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
