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

import os

from src.utils.command.command_executor import CommandExecutor
from src.utils.log.logger_generator import LoggerGenerator


class RunAction:
    def __init__(self, action: str, tasks: list, project: str, **kwargs):
        """
        执行指定项目的指定方法。

        :param action: 方法名称
        :param tasks: 任务列表
        :param project: 项目目录路径
        :param kwargs: 可选参数，包括:
            - debug: bool, 是否启用调试模式 (默认False)
            - time: bool, 是否记录任务时间 (默认False)
            - local: bool, 是否部署到本地 (默认False)
            以及其他自定义参数
        """
        self.action = action
        self.tasks = tasks
        self.project = project
        self.debug = kwargs.get('debug', False)
        self.time = kwargs.get('time', False)
        self.local = kwargs.get('local', False)
        self.log = LoggerGenerator().get_logger('run_action')

    def run(self) -> bool:
        """
        执行指定项目的指定方法。

        :return: 是否执行成功
        """
        self.log.debug(f'Running {self.action} action for {self.project}')
        for task in self.tasks:
            if not isinstance(task, dict):
                self.log.error(f'Unrecognized task: {task}')
                return False
            if 'name' in task:
                self.log.debug(f'Running task: {task["name"]}')
            else:
                self.log.debug(f'Running task: No Name Task')
            if 'playbook' in task:
                if not self._run_playbook(task, self.project):
                    return False
            else:
                self.log.error(f'Unrecognized task: {task}')
                return False
        return True

    def _run_playbook(self, task: dict, project: str) -> bool:
        if self.debug and task.get('disabled_in_debug', False):
            self.log.info(f'Skipping task "{task.get("name", "unamed task")}"')
            return True
        
        self.log.info(f'Running task {task.get("name", "")}')
        workspace = os.path.join(project, 'workspace')
        playbook = os.path.join(workspace, task['playbook'])
        if not os.path.exists(playbook):
            self.log.error(f'Playbook does not exist: {os.path.abspath(playbook)}')
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
        if self.local:
            cmd.extend(['--connection=local'])
        
        env = os.environ.copy()
        if self.time:
            env['ANSIBLE_CALLBACK_WHITELIST'] = 'profile_tasks'

        self.log.debug(f'Executing cmd: {cmd}')
        try:
            out, err, ret = CommandExecutor.run_single_cmd(cmd, print_on_console=True, env=env)
            self.log.debug('Execution log:\n' + out)
            if ret != 0:
                self.log.error(f'Execute cmd failed [code:{ret}]:\nSTDOUT: {out}\nSTDERR: {err}')
                return False
        except Exception as e:
            self.log.error(f'Exception occurred: {str(e)}')
            return False
        self.log.info(f'Execute succeeded: {task.get("name", "unamed task")}')
        return True
