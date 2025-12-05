# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.

import unittest
import os
import tempfile
import shutil
import yaml
from unittest.mock import patch, MagicMock
from src.commands.info.info_cmd import InfoCmd
from src.exceptions.config_exception import ConfigException


class TestInfoCmd(unittest.TestCase):
    def setUp(self):
        # 创建临时项目目录
        self.test_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.test_dir, "test_project")
        os.makedirs(self.project_path)
        
        # 创建有效的main.yaml
        self.main_yaml = os.path.join(self.project_path, "main.yaml")
        with open(self.main_yaml, 'w') as f:
            yaml.dump({
                "name": "test_project",
                "version": "1.0.0",
                "description": "Test project description",
                "action": {
                    "install": {
                        "description": "Install the application",
                        "tasks": [
                            {"name": "setup", "playbook": "setup.yml"}
                        ]
                    },
                    "uninstall": {
                        "description": "Uninstall the application",
                        "tasks": [
                            {"name": "cleanup", "playbook": "cleanup.yml"}
                        ]
                    }
                }
            }, f)
    
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """测试InfoCmd初始化"""
        info_cmd = InfoCmd(self.project_path)
        self.assertEqual(info_cmd.project, self.project_path)
        self.assertIsNotNone(info_cmd.log)
    
    def test_run_success(self):
        """测试成功获取项目信息"""
        info_cmd = InfoCmd(self.project_path)
        result = info_cmd.run()
        self.assertTrue(result)
    
    def test_run_with_invalid_project(self):
        """测试无效项目路径"""
        info_cmd = InfoCmd("/nonexistent/project")
        result = info_cmd.run()
        self.assertFalse(result)
    
    def test_run_with_missing_main_yaml(self):
        """测试缺少main.yaml文件"""
        os.remove(self.main_yaml)
        info_cmd = InfoCmd(self.project_path)
        result = info_cmd.run()
        self.assertFalse(result)
    
    def test_run_with_invalid_main_yaml(self):
        """测试无效的main.yaml文件"""
        with open(self.main_yaml, 'w') as f:
            f.write("invalid yaml content: [unclosed")
        
        info_cmd = InfoCmd(self.project_path)
        # yaml解析错误会抛出异常，被MainReader捕获并记录日志
        # 但实际会在MainReader初始化时抛出异常而不是返回False
        with self.assertRaises(Exception):
            result = info_cmd.run()
    
    def test_run_with_missing_fields(self):
        """测试main.yaml缺少必要字段（实际代码能容错处理）"""
        with open(self.main_yaml, 'w') as f:
            yaml.dump({
                "name": "test_project"
                # 缺少version, description, action等字段
            }, f)
        
        info_cmd = InfoCmd(self.project_path)
        # 实际代码能够容错处理缺少的字段，返回空值
        result = info_cmd.run()
        self.assertTrue(result)
    
    def test_run_with_empty_action(self):
        """测试action字段为空"""
        with open(self.main_yaml, 'w') as f:
            yaml.dump({
                "name": "test_project",
                "version": "1.0.0",
                "description": "Test project",
                "action": {}
            }, f)
        
        info_cmd = InfoCmd(self.project_path)
        result = info_cmd.run()
        self.assertTrue(result)  # 空action也应该能正常处理
    
    def test_run_with_multiple_actions(self):
        """测试多个action"""
        with open(self.main_yaml, 'w') as f:
            yaml.dump({
                "name": "test_project",
                "version": "2.0.0",
                "description": "Test project with multiple actions",
                "action": {
                    "install": {"description": "Install"},
                    "uninstall": {"description": "Uninstall"},
                    "update": {"description": "Update"},
                    "configure": {"description": "Configure"}
                }
            }, f)
        
        info_cmd = InfoCmd(self.project_path)
        result = info_cmd.run()
        self.assertTrue(result)
    
    def test_run_with_action_no_description(self):
        """测试action没有description字段"""
        with open(self.main_yaml, 'w') as f:
            yaml.dump({
                "name": "test_project",
                "version": "1.0.0",
                "description": "Test project",
                "action": {
                    "install": {
                        "tasks": [{"name": "setup", "playbook": "setup.yml"}]
                    }
                }
            }, f)
        
        info_cmd = InfoCmd(self.project_path)
        result = info_cmd.run()
        self.assertTrue(result)
    
    @patch('src.commands.info.info_cmd.MainReader')
    def test_run_with_config_exception(self, mock_reader):
        """测试MainReader抛出ConfigException"""
        mock_reader.side_effect = ConfigException("Config error")
        info_cmd = InfoCmd(self.project_path)
        result = info_cmd.run()
        self.assertFalse(result)

