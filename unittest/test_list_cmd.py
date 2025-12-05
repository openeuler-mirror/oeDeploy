# -*- coding: utf-8 -*-
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.

import unittest
import os
import tempfile
import yaml
import src.constants.paths
from unittest.mock import patch, MagicMock
from src.commands.list.list_cmd import ListCmd
from src.constants.paths import REPO_CACHE_DIR

class TestListCmd(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_dir = os.path.join(self.test_dir.name, "repo_cache")
        os.makedirs(self.repo_dir)
        
        # 创建测试yaml文件
        self.valid_yaml = os.path.join(self.repo_dir, "test_repo.yaml")
        with open(self.valid_yaml, 'w') as f:
            yaml.dump({
                "plugins": [
                    {
                        "test_plugin": [
                            {
                                "name": "test_plugin",
                                "version": "1.0.0",
                                "updated": "2025-01-01T00:00:00+0800",
                                "type": "app",
                                "size": 10240,
                                "description": "Test Description"
                            }
                        ]
                    }
                ]
            }, f)
            
        # 模拟REPO_CACHE_DIR
        self.original_repo_cache = src.constants.paths.REPO_CACHE_DIR
        src.constants.paths.REPO_CACHE_DIR = self.repo_dir
        
    def tearDown(self):
        self.test_dir.cleanup()
        src.constants.paths.REPO_CACHE_DIR = self.original_repo_cache

    def test_run_with_invalid_source(self):
        """测试无效源目录"""
        with patch('src.commands.list.list_cmd.REPO_CACHE_DIR', "/non/existent/path"):
            lc = ListCmd()
            result = lc.run()
            self.assertFalse(result)

    def test_run_with_empty_source(self):
        """测试空插件目录"""
        empty_dir = os.path.join(self.test_dir.name, "empty")
        os.makedirs(empty_dir)
        with patch('src.commands.list.list_cmd.REPO_CACHE_DIR', empty_dir):
            lc = ListCmd()
            result = lc.run()
            self.assertTrue(result)

    def test_run_with_valid_plugin(self):
        """测试有效插件解析"""
        lc = ListCmd()
        result = lc.run()
        self.assertTrue(result)

    def test_run_with_invalid_yaml(self):
        """测试无效yaml文件"""
        invalid_yaml = os.path.join(self.repo_dir, "invalid.yaml")
        with open(invalid_yaml, 'w') as f:
            f.write("invalid: yaml: content:")
            
        lc = ListCmd()
        result = lc.run()
        self.assertTrue(result)  # 应该能处理错误继续执行

    def test_run_with_empty_plugin(self):
        """测试空插件文件"""
        empty_yaml = os.path.join(self.repo_dir, "empty.yaml")
        with open(empty_yaml, 'w') as f:
            yaml.dump({}, f)
            
        lc = ListCmd()
        result = lc.run()
        self.assertTrue(result)
    
    def test_create_table(self):
        """测试创建表格"""
        lc = ListCmd()
        table = lc._create_table()
        self.assertIsNotNone(table)
        self.assertEqual(table.field_names, ["repo", "name", "version", "updated", "type", "size", "description"])
    
    def test_process_yaml_file_success(self):
        """测试处理yaml文件成功"""
        lc = ListCmd()
        table = lc._create_table()
        result = lc._process_yaml_file(self.valid_yaml, "test_repo", table)
        self.assertTrue(result)
    
    def test_process_yaml_file_no_plugins(self):
        """测试处理没有plugins字段的yaml文件"""
        no_plugins_yaml = os.path.join(self.repo_dir, "no_plugins.yaml")
        with open(no_plugins_yaml, 'w') as f:
            yaml.dump({"other": "data"}, f)
        
        lc = ListCmd()
        table = lc._create_table()
        result = lc._process_yaml_file(no_plugins_yaml, "test_repo", table)
        self.assertFalse(result)
    
    def test_process_yaml_file_with_multiple_versions(self):
        """测试处理包含多个版本的插件"""
        multi_version_yaml = os.path.join(self.repo_dir, "multi_version.yaml")
        with open(multi_version_yaml, 'w') as f:
            yaml.dump({
                "plugins": [
                    {
                        "my_plugin": [
                            {
                                "name": "my_plugin",
                                "version": "2.0.0",
                                "updated": "2025-02-01T00:00:00+0800",
                                "type": "app",
                                "size": 20480,
                                "description": "Version 2.0"
                            },
                            {
                                "name": "my_plugin",
                                "version": "1.0.0",
                                "updated": "2025-01-01T00:00:00+0800",
                                "type": "app",
                                "size": 10240,
                                "description": "Version 1.0"
                            }
                        ]
                    }
                ]
            }, f)
        
        lc = ListCmd()
        table = lc._create_table()
        result = lc._process_yaml_file(multi_version_yaml, "test_repo", table)
        self.assertTrue(result)
    
    def test_non_yaml_files_ignored(self):
        """测试非yaml文件被忽略"""
        txt_file = os.path.join(self.repo_dir, "test.txt")
        with open(txt_file, 'w') as f:
            f.write("not a yaml file")
        
        lc = ListCmd()
        result = lc.run()
        self.assertTrue(result)
    
    def test_process_yaml_file_with_missing_fields(self):
        """测试处理缺少某些字段的插件信息"""
        partial_yaml = os.path.join(self.repo_dir, "partial.yaml")
        with open(partial_yaml, 'w') as f:
            yaml.dump({
                "plugins": [
                    {
                        "partial_plugin": [
                            {
                                "name": "partial_plugin",
                                "version": "1.0.0"
                                # 缺少其他字段
                            }
                        ]
                    }
                ]
            }, f)
        
        lc = ListCmd()
        table = lc._create_table()
        result = lc._process_yaml_file(partial_yaml, "test_repo", table)
        self.assertTrue(result)
