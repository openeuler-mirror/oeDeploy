# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
# ======================================================================================================================

from src.commands.run.run_action import RunAction
from src.exceptions.config_exception import ConfigException
from src.utils.log.logger_generator import LoggerGenerator
from src.utils.main_reader import MainReader


class RunCmd:
    def __init__(self, action: str, project: str):
        """
        执行一个项目中的方法。

        :param action: 方法名称
        :param project: 项目目录路径
        """
        self.action = action
        self.project = project
        self.log = LoggerGenerator().get_logger('run_cmd')

    def run(self):
        """
        执行一个项目中的方法。

        :return: 是否执行成功
        """
        self.log.info(f'Running cmd run: action={self.action}, project={self.project}')
        try:
            main = MainReader(self.project)
            action = main.get_action_detail(self.action)
        except ConfigException as e:
            self.log.error(f'Failed to get project main info: {e}')
            return False
        tasks = action['tasks']
        return RunAction(self.project, self.action, tasks).run()
