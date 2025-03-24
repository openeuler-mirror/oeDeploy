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
# Create: 2025-03-17
# ======================================================================================================================

#run as:PYTHONPATH=/home/xxx/openeuler_repos/oeDeploy/oedp coverage run -m pytest

import unittest
from unittest.mock import patch, MagicMock
from src.commands.run.run_action import RunAction
from src.utils.command.command_executor import CommandExecutor
import os

class TestRunAction(unittest.TestCase):
    def setUp(self):
        self.project_path = "/fake/project"
        self.action_name = "deploy"
        self.valid_task = {
            "playbook": "install.yml",
            "vars": "variables.yml",
            "scope": "nodes"
        }


    @patch('src.commands.run.run_action.os.path.exists')
    def test_missing_playbook(self, mock_exists):
        """测试playbook文件不存在的情况"""
        mock_exists.return_value = False
        tasks = [self.valid_task]
        
        runner = RunAction(self.project_path, self.action_name, tasks)
        result = runner.run()
        
        self.assertFalse(result)

    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_command_failure(self, mock_cmd):
        """测试命令执行失败的情况"""
        mock_cmd.return_value = ("", "Permission denied", 1)
        tasks = [self.valid_task]
        
        runner = RunAction(self.project_path, self.action_name, tasks)
        result = runner.run()
        
        self.assertFalse(result)

    def test_disabled_task(self):
        """测试跳过被禁用的任务"""
        disabled_task = {**self.valid_task, "disabled": True}
        runner = RunAction(self.project_path, self.action_name, [disabled_task])
        
        with self.assertLogs(level='INFO') as log:
            result = runner.run()
            
        self.assertTrue(result)
        self.assertIn('Skipping task', log.output[0])

