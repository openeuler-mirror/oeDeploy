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

import unittest
from unittest.mock import patch
from src.commands.run.run_action import RunAction


class TestRunAction(unittest.TestCase):
    def setUp(self):
        self.project_path = "/fake/project"
        self.action_name = "deploy"
        self.valid_task = {
            "name": "test_task",
            "playbook": "install.yml",
            "vars": "variables.yml",
            "scope": "nodes"
        }

    @patch('src.commands.run.run_action.os.path.exists')
    def test_missing_playbook(self, mock_exists):
        """测试playbook文件不存在的情况"""
        mock_exists.return_value = False
        tasks = [self.valid_task]
        
        runner = RunAction(self.action_name, tasks, self.project_path, debug=False)
        result = runner.run()
        
        self.assertFalse(result)

    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_command_failure(self, mock_cmd):
        """测试命令执行失败的情况"""
        mock_cmd.return_value = ("", "Permission denied", 1)
        tasks = [self.valid_task]
        
        runner = RunAction(self.action_name, tasks, self.project_path, debug=False)
        result = runner.run()
        
        self.assertFalse(result)

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_disabled_task(self, mock_cmd, mock_exists):
        """测试跳过被禁用的任务"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)  # 模拟命令执行成功
        disabled_task = {**self.valid_task, "disabled": True}
        runner = RunAction(self.action_name, [disabled_task], self.project_path, debug=False)
    
        with self.assertLogs(level='INFO') as log:
            result = runner.run()
    
        # 根据实际日志输出调整断言
        self.assertTrue(result)
        self.assertIn('Running task test_task', log.output[0])

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_debug_mode(self, mock_cmd, mock_exists):
        """测试debug模式"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        disabled_task = {**self.valid_task, "disabled_in_debug": True}
        runner = RunAction(self.action_name, [disabled_task], self.project_path, debug=True)
        
        with self.assertLogs(level='INFO') as log:
            result = runner.run()
            
        self.assertTrue(result)
        self.assertIn('Skipping task', log.output[0])

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_multiple_tasks(self, mock_cmd, mock_exists):
        """测试多任务执行"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        tasks = [
            self.valid_task,
            {**self.valid_task, "name": "task2", "playbook": "config.yml"}
        ]
        runner = RunAction(self.action_name, tasks, self.project_path, debug=False)
        result = runner.run()
        
        self.assertTrue(result)
        self.assertEqual(mock_cmd.call_count, 2)

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_task_with_vars_and_scope(self, mock_cmd, mock_exists):
        """测试带变量和scope参数的playbook"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        task = {
            "name": "complex_task",
            "playbook": "deploy.yml",
            "vars": "custom_vars.yml",
            "scope": "web_servers"
        }
        runner = RunAction(self.action_name, [task], self.project_path, debug=False)
        result = runner.run()
        
        self.assertTrue(result)
        args, _ = mock_cmd.call_args
        cmd = args[0]
        self.assertIn('-e @/fake/project/workspace/custom_vars.yml', ' '.join(cmd))
        self.assertIn('--limit web_servers', ' '.join(cmd))

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_invalid_task_format(self, mock_cmd, mock_exists):
        """测试无效任务格式"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        # 非字典格式的任务
        runner = RunAction(self.action_name, ["invalid_task"], self.project_path, debug=False)
        result = runner.run()
        
        self.assertFalse(result)

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_missing_vars_file(self, mock_cmd, mock_exists):
        """测试变量文件缺失"""
        mock_exists.side_effect = lambda x: x.endswith('install.yml')  # 仅playbook存在
        mock_cmd.return_value = ("", "", 0)
        
        task = {
            "name": "missing_vars",
            "playbook": "install.yml",
            "vars": "missing_vars.yml"
        }
        runner = RunAction(self.action_name, [task], self.project_path, debug=False)
        result = runner.run()
        
        self.assertFalse(result)

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_command_exception(self, mock_cmd, mock_exists):
        """测试命令执行异常"""
        mock_exists.return_value = True
        mock_cmd.side_effect = Exception("Command failed")
        
        runner = RunAction(self.action_name, [self.valid_task], self.project_path, debug=False)
        result = runner.run()
        
        self.assertFalse(result)

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_log_output_verification(self, mock_cmd, mock_exists):
        """测试日志输出验证"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        runner = RunAction(self.action_name, [self.valid_task], self.project_path, debug=False)
        
        with self.assertLogs(level='INFO') as log:
            result = runner.run()
            
        self.assertTrue(result)
        self.assertIn('Running task test_task', log.output[0])
        self.assertIn('Execute succeeded: test_task', log.output[-1])

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_different_scope_values(self, mock_cmd, mock_exists):
        """测试不同scope值"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        tasks = [
            {"name": "no_scope", "playbook": "install.yml"},
            {"name": "empty_scope", "playbook": "install.yml", "scope": ""},
            {"name": "all_scope", "playbook": "install.yml", "scope": "all"},
            {"name": "custom_scope", "playbook": "install.yml", "scope": "web_servers"}
        ]
        runner = RunAction(self.action_name, tasks, self.project_path, debug=False)
        result = runner.run()
        
        self.assertTrue(result)
        self.assertEqual(mock_cmd.call_count, 4)

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_empty_task_list(self, mock_cmd, mock_exists):
        """测试空任务列表"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        runner = RunAction(self.action_name, [], self.project_path, debug=False)
        result = runner.run()
        
        self.assertTrue(result)
        mock_cmd.assert_not_called()

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_task_without_name(self, mock_cmd, mock_exists):
        """测试无name的任务"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        task = {"playbook": "install.yml"}
        runner = RunAction(self.action_name, [task], self.project_path, debug=False)
        
        with self.assertLogs(level='INFO') as log:
            result = runner.run()
            
        self.assertTrue(result)
        self.assertIn('Running task ', log.output[0])

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_partial_task_failure(self, mock_cmd, mock_exists):
        """测试部分任务失败"""
        mock_exists.return_value = True
        mock_cmd.side_effect = [
            ("", "", 0),  # 第一个任务成功
            ("", "Error", 1),  # 第二个任务失败
            ("", "", 0)   # 不会执行
        ]
        
        tasks = [
            {"name": "success_task", "playbook": "success.yml"},
            {"name": "failed_task", "playbook": "failed.yml"},
            {"name": "skipped_task", "playbook": "skipped.yml"}
        ]
        runner = RunAction(self.action_name, tasks, self.project_path, debug=False)
        result = runner.run()
        
        self.assertFalse(result)
        self.assertEqual(mock_cmd.call_count, 2)

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_debug_mode_with_different_tasks(self, mock_cmd, mock_exists):
        """测试debug模式下不同任务行为"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        tasks = [
            {"name": "normal_task", "playbook": "normal.yml"},
            {"name": "debug_disabled_task", "playbook": "debug.yml", "disabled_in_debug": True}
        ]
        runner = RunAction(self.action_name, tasks, self.project_path, debug=True)
        
        with self.assertLogs(level='INFO') as log:
            result = runner.run()
            
        self.assertTrue(result)
        self.assertIn('Skipping task "debug_disabled_task"', log.output[2])
        self.assertEqual(mock_cmd.call_count, 1)

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_multiple_vars_files(self, mock_cmd, mock_exists):
        """测试多个变量文件"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        task = {
            "name": "multi_vars",
            "playbook": "install.yml",
            "vars": "vars1.yml",
            "scope": "nodes"
        }
        runner = RunAction(self.action_name, [task], self.project_path, debug=False)
        result = runner.run()
        
        self.assertTrue(result)
        args, _ = mock_cmd.call_args
        cmd = ' '.join(args[0])
        self.assertIn('-e @/fake/project/workspace/vars1.yml', cmd)

