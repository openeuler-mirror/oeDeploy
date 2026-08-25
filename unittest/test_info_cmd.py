# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.

import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import yaml

from src.commands.info.info_cmd import InfoCmd
from src.exceptions.config_exception import ConfigException


class TestInfoCmd(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试项目结构
        self.test_project_dir = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.test_project_dir)
        
        # 创建main.yaml文件
        self.main_content = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin for unit testing",
            "action": {
                "install": {
                    "description": "Install the plugin"
                },
                "uninstall": {
                    "description": "Uninstall the plugin"
                },
                "setup": {
                    "description": "Setup the plugin configuration"
                }
            }
        }
        with open(os.path.join(self.test_project_dir, "main.yaml"), 'w') as f:
            yaml.dump(self.main_content, f)

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        """测试InfoCmd初始化"""
        info_cmd = InfoCmd(self.test_project_dir)
        self.assertEqual(info_cmd.project, self.test_project_dir)
        self.assertIsNotNone(info_cmd.log)

    def test_run_success(self):
        """测试run方法（成功）"""
        info_cmd = InfoCmd(self.test_project_dir)
        result = info_cmd.run()
        
        self.assertTrue(result)

    def test_run_missing_main_file(self):
        """测试run方法（缺少main.yaml文件）"""
        # 删除main.yaml文件
        os.remove(os.path.join(self.test_project_dir, "main.yaml"))
        
        info_cmd = InfoCmd(self.test_project_dir)
        result = info_cmd.run()
        
        self.assertFalse(result)

    def test_run_invalid_main_yaml(self):
        """测试run方法（无效的main.yaml内容）"""
        # 写入无效的YAML内容
        with open(os.path.join(self.test_project_dir, "main.yaml"), 'w') as f:
            f.write("invalid yaml content: [")
        
        info_cmd = InfoCmd(self.test_project_dir)
        with self.assertRaises(Exception):
            info_cmd.run()

    def test_run_missing_project_directory(self):
        """测试run方法（项目目录不存在）"""
        info_cmd = InfoCmd("/invalid/path")
        result = info_cmd.run()
        
        self.assertFalse(result)

    def test_get_name_success(self):
        """测试获取名称（成功）"""
        info_cmd = InfoCmd(self.test_project_dir)
        
        with patch('src.commands.info.info_cmd.MainReader') as mock_main_reader:
            mock_main = MagicMock()
            mock_main.get_name.return_value = "test_plugin"
            mock_main.get_version.return_value = "1.0.0"
            mock_main.get_description.return_value = "Test description"
            mock_main.get_action.return_value = {
                "install": {"description": "Install"},
                "uninstall": {"description": "Uninstall"}
            }
            mock_main_reader.return_value = mock_main
            
            result = info_cmd.run()
            
            self.assertTrue(result)
            mock_main.get_name.assert_called_once()
            mock_main.get_version.assert_called_once()
            mock_main.get_description.assert_called_once()
            mock_main.get_action.assert_called_once()

    def test_get_name_missing(self):
        """测试获取名称（名称缺失）"""
        # 创建缺少name字段的main.yaml
        main_content = {
            "version": "1.0.0",
            "description": "Test plugin",
            "action": {
                "install": {"description": "Install"}
            }
        }
        with open(os.path.join(self.test_project_dir, "main.yaml"), 'w') as f:
            yaml.dump(main_content, f)
        
        info_cmd = InfoCmd(self.test_project_dir)
        result = info_cmd.run()
        
        self.assertFalse(result)

    def test_get_version_missing(self):
        """测试获取版本（版本缺失）"""
        # 创建缺少version字段的main.yaml
        main_content = {
            "name": "test_plugin",
            "description": "Test plugin",
            "action": {
                "install": {"description": "Install"}
            }
        }
        with open(os.path.join(self.test_project_dir, "main.yaml"), 'w') as f:
            yaml.dump(main_content, f)
        
        info_cmd = InfoCmd(self.test_project_dir)
        result = info_cmd.run()
        
        self.assertTrue(result)  # version是可选的，应该成功

    def test_get_description_missing(self):
        """测试获取描述（描述缺失）"""
        # 创建缺少description字段的main.yaml
        main_content = {
            "name": "test_plugin",
            "version": "1.0.0",
            "action": {
                "install": {"description": "Install"}
            }
        }
        with open(os.path.join(self.test_project_dir, "main.yaml"), 'w') as f:
            yaml.dump(main_content, f)
        
        info_cmd = InfoCmd(self.test_project_dir)
        result = info_cmd.run()
        
        self.assertTrue(result)  # description是可选的，应该成功

    def test_get_action_missing(self):
        """测试获取操作（操作缺失）"""
        # 创建缺少action字段的main.yaml
        main_content = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin"
        }
        with open(os.path.join(self.test_project_dir, "main.yaml"), 'w') as f:
            yaml.dump(main_content, f)
        
        info_cmd = InfoCmd(self.test_project_dir)
        result = info_cmd.run()
        
        self.assertTrue(result)  # action是可选的，应该成功

    def test_action_list_generation(self):
        """测试操作列表生成"""
        info_cmd = InfoCmd(self.test_project_dir)
        
        with patch('src.commands.info.info_cmd.MainReader') as mock_main_reader:
            mock_main = MagicMock()
            mock_main.get_name.return_value = "test_plugin"
            mock_main.get_version.return_value = "1.0.0"
            mock_main.get_description.return_value = "Test description"
            mock_main.get_action.return_value = {
                "install": {"description": "Install the plugin"},
                "uninstall": {"description": "Uninstall the plugin"},
                "setup": {"description": "Setup configuration"}
            }
            mock_main_reader.return_value = mock_main
            
            result = info_cmd.run()
            
            self.assertTrue(result)

    def test_empty_action_list(self):
        """测试空操作列表"""
        # 创建空action的main.yaml
        main_content = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "action": {}
        }
        with open(os.path.join(self.test_project_dir, "main.yaml"), 'w') as f:
            yaml.dump(main_content, f)
        
        info_cmd = InfoCmd(self.test_project_dir)
        result = info_cmd.run()
        
        self.assertTrue(result)

    def test_action_without_description(self):
        """测试没有描述的操作"""
        # 创建缺少操作描述的main.yaml
        main_content = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "action": {
                "install": {},
                "uninstall": {"description": "Uninstall"}
            }
        }
        with open(os.path.join(self.test_project_dir, "main.yaml"), 'w') as f:
            yaml.dump(main_content, f)
        
        info_cmd = InfoCmd(self.test_project_dir)
        result = info_cmd.run()
        
        self.assertTrue(result)

    def test_config_exception_handling(self):
        """测试配置异常处理"""
        info_cmd = InfoCmd(self.test_project_dir)
        
        with patch('src.commands.info.info_cmd.MainReader') as mock_main_reader:
            mock_main_reader.side_effect = ConfigException("Test exception")
            
            result = info_cmd.run()
            
            self.assertFalse(result)

    def test_general_exception_handling(self):
        """测试通用异常处理"""
        info_cmd = InfoCmd(self.test_project_dir)
        
        with patch('src.commands.info.info_cmd.MainReader') as mock_main_reader:
            mock_main_reader.side_effect = Exception("Unexpected error")
            with self.assertRaises(Exception):
                info_cmd.run()

    def test_table_formatting(self):
        """测试表格格式化"""
        info_cmd = InfoCmd(self.test_project_dir)
        
        with patch('src.commands.info.info_cmd.MainReader') as mock_main_reader:
            mock_main = MagicMock()
            mock_main.get_name.return_value = "test_plugin"
            mock_main.get_version.return_value = "1.0.0"
            mock_main.get_description.return_value = "Test description"
            mock_main.get_action.return_value = {
                "install": {"description": "Install the plugin with a very long description that might wrap in the table"},
                "uninstall": {"description": "Uninstall"}
            }
            mock_main_reader.return_value = mock_main
            
            result = info_cmd.run()
            
            self.assertTrue(result)

    def test_project_path_normalization(self):
        """测试项目路径标准化"""
        # 测试相对路径
        relative_path = "."
        info_cmd = InfoCmd(relative_path)
        self.assertEqual(info_cmd.project, relative_path)
        
        # 测试绝对路径
        absolute_path = os.path.abspath(self.test_project_dir)
        info_cmd = InfoCmd(absolute_path)
        self.assertEqual(info_cmd.project, absolute_path)

    @patch('src.commands.info.info_cmd.LoggerGenerator')
    def test_logger_initialization(self, mock_logger_generator):
        """测试日志生成器初始化"""
        mock_logger = MagicMock()
        mock_logger_generator.return_value.get_logger.return_value = mock_logger
        
        info_cmd = InfoCmd(self.test_project_dir)
        
        mock_logger_generator.return_value.get_logger.assert_called_once_with('info_cmd')
        self.assertEqual(info_cmd.log, mock_logger)


if __name__ == '__main__':
    unittest.main()
