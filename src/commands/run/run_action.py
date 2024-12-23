# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
# ======================================================================================================================

import os

from src.utils.command.command_executor import CommandExecutor
from src.utils.log.logger_generator import LoggerGenerator


class RunAction:
    def __init__(self, project: str, action: str, tasks: list):
        """
        执行指定项目的指定方法。

        :param project: 项目目录路径
        :param action: 方法名称
        :param tasks: 方法代码路径
        """
        self.project = project
        self.action = action
        self.tasks = tasks
        self.log = LoggerGenerator().get_logger('run_action')

    def run(self) -> bool:
        """
        执行指定项目的指定方法。

        :return: 是否执行成功
        """
        self.log.info(f'Running {self.action} action for {self.project}')
        for task in self.tasks:
            if not isinstance(task, dict):
                self.log.error(f'Unrecognized task: {task}')
                return False
            if 'name' in task:
                self.log.info(f'Running task: {task["name"]}')
            else:
                self.log.info(f'Running task: No Name Task')
            if 'playbook' in task:
                return self._run_playbook(task, self.project)
            else:
                self.log.error(f'Unrecognized task: {task}')
                return False

    def _run_playbook(self, task: dict, project: str) -> bool:
        workspace = os.path.join(project, 'workspace')
        playbook = os.path.join(workspace, task['playbook'])
        if not os.path.exists(playbook):
            self.log.error(f'Playbook {playbook} does not exist')
            return False
        inventory = os.path.join(project, 'config.yaml')
        cmd = ['ansible-playbook', playbook, '-i', inventory]
        if 'vars' in task:
            variables = os.path.join(workspace, task['vars'])
            if not os.path.exists(variables):
                self.log.error(f'Vars {variables} does not exist')
                return False
            cmd.extend(['-e', f'@{variables}'])
        if 'scope' in task and task['scope'] != 'all':
            cmd.extend(['--limit', task['scope']])
        self.log.info(f'Executing cmd: {cmd}')
        out, err, ret = CommandExecutor.run_single_cmd(cmd, print_on_console=True)
        if ret:
            if err:
                self.log.error(f'Execute cmd failed: {err}')
            else:
                self.log.error(f'Execute cmd failed')
            return False
        self.log.info(f'Execute succeeded')
        return True
