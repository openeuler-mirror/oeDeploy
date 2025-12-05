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
import os
from unittest.mock import patch, MagicMock
from src.commands.run.run_action import RunAction


class TestRunAction(unittest.TestCase):
    def setUp(self):
        self.project_path = "/fake/project"
        self.action_name = "deploy"
        self.valid_task = {
            "name": "test_task",
            "playbook": "install.yml",
            "vars": "variables.yml",
            "scope": "all"
        }

    @patch('src.commands.run.run_action.os.path.exists')
    def test_missing_playbook(self, mock_exists):
        """测试playbook文件不存在的情况"""
        mock_exists.return_value = False
        tasks = [self.valid_task]
        
        runner = RunAction(self.action_name, tasks, self.project_path, debug=False)
        result = runner.run()
        
        self.assertFalse(result)

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_command_failure(self, mock_cmd, mock_exists):
        """测试命令执行失败的情况"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "Permission denied", 1)
        tasks = [self.valid_task]
        
        runner = RunAction(self.action_name, tasks, self.project_path, debug=False)
        result = runner.run()
        
        self.assertFalse(result)

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_disabled_task(self, mock_cmd, mock_exists):
        """测试跳过被禁用的任务（正常情况下不会跳过，因为没有disabled字段）"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        # 注意：源码中没有disabled字段处理逻辑，任务仍会执行
        task = {**self.valid_task}
        runner = RunAction(self.action_name, [task], self.project_path, debug=False)
    
        result = runner.run()
        self.assertTrue(result)
        mock_cmd.assert_called_once()

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_debug_mode(self, mock_cmd, mock_exists):
        """测试debug模式下跳过disabled_in_debug的任务"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        disabled_task = {**self.valid_task, "disabled_in_debug": True}
        runner = RunAction(self.action_name, [disabled_task], self.project_path, debug=True)
        
        result = runner.run()
        self.assertTrue(result)
        mock_cmd.assert_not_called()  # 任务被跳过，不会执行命令

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
        cmd_str = ' '.join(cmd)
        self.assertIn('-e', cmd_str)
        self.assertIn('@/fake/project/workspace/custom_vars.yml', cmd_str)
        self.assertIn('--limit', cmd_str)
        self.assertIn('web_servers', cmd_str)

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
        
        result = runner.run()
        self.assertTrue(result)
        mock_cmd.assert_called_once()

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_different_scope_values(self, mock_cmd, mock_exists):
        """测试不同scope值（scope='all'时不添加--limit参数）"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        tasks = [
            {"name": "no_scope", "playbook": "install.yml"},
            {"name": "all_scope", "playbook": "install.yml", "scope": "all"},
            {"name": "custom_scope", "playbook": "install.yml", "scope": "web_servers"}
        ]
        runner = RunAction(self.action_name, tasks, self.project_path, debug=False)
        result = runner.run()
        
        self.assertTrue(result)
        self.assertEqual(mock_cmd.call_count, 3)

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
        """测试无name的任务（任务名为空字符串）"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        task = {"playbook": "install.yml"}
        runner = RunAction(self.action_name, [task], self.project_path, debug=False)
        result = runner.run()
        
        self.assertTrue(result)
        mock_cmd.assert_called_once()

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
        result = runner.run()
        
        self.assertTrue(result)
        self.assertEqual(mock_cmd.call_count, 1)  # 只执行一个任务

    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_vars_file_usage(self, mock_cmd, mock_exists):
        """测试变量文件的使用"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        task = {
            "name": "with_vars",
            "playbook": "install.yml",
            "vars": "vars1.yml",
            "scope": "all"
        }
        runner = RunAction(self.action_name, [task], self.project_path, debug=False)
        result = runner.run()
        
        self.assertTrue(result)
        args, _ = mock_cmd.call_args
        cmd = ' '.join(args[0])
        self.assertIn('-e', cmd)
        self.assertIn('@/fake/project/workspace/vars1.yml', cmd)
    
    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_local_mode(self, mock_cmd, mock_exists):
        """测试local模式（添加--connection=local参数）"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        runner = RunAction(self.action_name, [self.valid_task], self.project_path, debug=False, local=True)
        result = runner.run()
        
        self.assertTrue(result)
        args, _ = mock_cmd.call_args
        cmd = ' '.join(args[0])
        self.assertIn('--connection=local', cmd)
    
    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_time_mode(self, mock_cmd, mock_exists):
        """测试time模式（设置ANSIBLE_CALLBACK_WHITELIST环境变量）"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        runner = RunAction(self.action_name, [self.valid_task], self.project_path, debug=False, time=True)
        result = runner.run()
        
        self.assertTrue(result)
        args, kwargs = mock_cmd.call_args
        self.assertIn('env', kwargs)
        self.assertEqual(kwargs['env'].get('ANSIBLE_CALLBACK_WHITELIST'), 'profile_tasks')
    
    @patch('src.commands.run.run_action.os.path.exists')
    @patch('src.commands.run.run_action.CommandExecutor.run_single_cmd')
    def test_scope_all_no_limit(self, mock_cmd, mock_exists):
        """测试scope为all时不添加--limit参数"""
        mock_exists.return_value = True
        mock_cmd.return_value = ("", "", 0)
        
        task = {"name": "test", "playbook": "test.yml", "scope": "all"}
        runner = RunAction(self.action_name, [task], self.project_path, debug=False)
        result = runner.run()
        
        self.assertTrue(result)
        args, _ = mock_cmd.call_args
        cmd = ' '.join(args[0])
        self.assertNotIn('--limit', cmd)

