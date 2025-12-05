# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.

import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import yaml

from src.commands.check.check_cmd import CheckCmd


class TestCheckCmd(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.project_path = "/fake/project"
        self.action = "install"
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试项目结构
        self.test_project_dir = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.test_project_dir)
        os.makedirs(os.path.join(self.test_project_dir, "workspace"))
        
        # 创建config.yaml文件
        self.config_content = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin for unit testing",
            "all": {
                "vars": {
                    "test_var": "test_value"
                },
                "hosts": {
                    "localhost": {
                        "ansible_connection": "local"
                    }
                }
            }
        }
        with open(os.path.join(self.test_project_dir, "config.yaml"), 'w') as f:
            yaml.dump(self.config_content, f)
        
        # 创建main.yaml文件
        self.main_content = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin for unit testing",
            "action": {
                "install": {
                    "description": "Install the plugin",
                    "tasks": [
                        {
                            "name": "test_task",
                            "playbook": "install.yml"
                        }
                    ]
                }
            }
        }
        with open(os.path.join(self.test_project_dir, "main.yaml"), 'w') as f:
            yaml.dump(self.main_content, f)
        
        # 创建playbook文件
        playbook_content = {
            "name": "Test playbook",
            "hosts": "localhost",
            "tasks": [
                {
                    "name": "Test task",
                    "debug": {
                        "msg": "Hello World"
                    }
                }
            ]
        }
        with open(os.path.join(self.test_project_dir, "workspace", "install.yml"), 'w') as f:
            yaml.dump(playbook_content, f)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        """测试CheckCmd初始化"""
        check_cmd = CheckCmd(self.project_path, self.action)
        self.assertEqual(check_cmd.project, self.project_path)
        self.assertEqual(check_cmd.action, self.action)
        self.assertIsNotNone(check_cmd.log)

    def test_run_basic(self):
        """测试run方法基本功能"""
        check_cmd = CheckCmd(self.test_project_dir, "install")
        result = check_cmd.run()
        # 当前实现为pass，返回None
        self.assertIsNone(result)

    def test_run_with_invalid_project(self):
        """测试run方法（无效的项目路径）"""
        check_cmd = CheckCmd("/invalid/path", "install")
        result = check_cmd.run()
        self.assertIsNone(result)

    def test_run_with_missing_config(self):
        """测试run方法（缺少配置文件）"""
        # 删除config.yaml文件
        os.remove(os.path.join(self.test_project_dir, "config.yaml"))
        
        check_cmd = CheckCmd(self.test_project_dir, "install")
        result = check_cmd.run()
        self.assertIsNone(result)

    def test_run_with_missing_main(self):
        """测试run方法（缺少main.yaml文件）"""
        # 删除main.yaml文件
        os.remove(os.path.join(self.test_project_dir, "main.yaml"))
        
        check_cmd = CheckCmd(self.test_project_dir, "install")
        result = check_cmd.run()
        self.assertIsNone(result)

    def test_run_with_missing_workspace(self):
        """测试run方法（缺少workspace目录）"""
        # 删除workspace目录
        shutil.rmtree(os.path.join(self.test_project_dir, "workspace"))
        
        check_cmd = CheckCmd(self.test_project_dir, "install")
        result = check_cmd.run()
        self.assertIsNone(result)

    def test_run_with_invalid_action(self):
        """测试run方法（无效的action）"""
        check_cmd = CheckCmd(self.test_project_dir, "invalid_action")
        result = check_cmd.run()
        self.assertIsNone(result)

    @patch('src.commands.check.check_cmd.LoggerGenerator')
    def test_logger_initialization(self, mock_logger_generator):
        """测试日志生成器初始化"""
        mock_logger = MagicMock()
        mock_logger_generator.return_value.get_logger.return_value = mock_logger
        
        check_cmd = CheckCmd(self.project_path, self.action)
        
        mock_logger_generator.return_value.get_logger.assert_called_once_with('check_cmd')
        self.assertEqual(check_cmd.log, mock_logger)

    def test_different_actions(self):
        """测试不同的action参数"""
        actions = ["install", "uninstall", "setup", "info"]
        
        for action in actions:
            with self.subTest(action=action):
                check_cmd = CheckCmd(self.test_project_dir, action)
                result = check_cmd.run()
                self.assertIsNone(result)

    def test_project_path_normalization(self):
        """测试项目路径标准化"""
        # 测试相对路径
        relative_path = "."
        check_cmd = CheckCmd(relative_path, self.action)
        self.assertEqual(check_cmd.project, relative_path)
        
        # 测试绝对路径
        absolute_path = os.path.abspath(self.test_project_dir)
        check_cmd = CheckCmd(absolute_path, self.action)
        self.assertEqual(check_cmd.project, absolute_path)

    def test_empty_project_path(self):
        """测试空项目路径"""
        check_cmd = CheckCmd("", self.action)
        self.assertEqual(check_cmd.project, "")
        result = check_cmd.run()
        self.assertIsNone(result)

    def test_none_project_path(self):
        """测试None项目路径"""
        check_cmd = CheckCmd(None, self.action)
        self.assertEqual(check_cmd.project, None)
        result = check_cmd.run()
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
