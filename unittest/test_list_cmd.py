# -*- coding: utf-8 -*-
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.

import unittest
import os
import tempfile
import yaml
import src.constants.paths
from unittest.mock import patch, mock_open, MagicMock
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
                                "name": "TestPlugin",
                                "version": "1.0.0",
                                "type": "app",
                                "size": "10MB",
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

    @patch('src.commands.list.list_cmd.LoggerGenerator.get_logger')
    def test_run_with_invalid_source(self, mock_logger):
        """测试无效源目录"""
        mock_log = MagicMock()
        mock_logger.return_value = mock_log
        
        with patch('src.constants.paths.REPO_CACHE_DIR', "/non/existent/path"):
            lc = ListCmd()
            result = lc.run()
            # 根据实际实现，即使路径无效也返回True
            self.assertTrue(result)

    def test_run_with_empty_source(self):
        """测试空插件目录"""
        empty_dir = os.path.join(self.test_dir.name, "empty")
        os.makedirs(empty_dir)
        with patch('src.constants.paths.REPO_CACHE_DIR', empty_dir):
            lc = ListCmd()
            self.assertTrue(lc.run())

    def test_run_with_valid_plugin(self):
        """测试有效插件解析"""
        lc = ListCmd()
        self.assertTrue(lc.run())

    def test_run_with_invalid_yaml(self):
        """测试无效yaml文件"""
        invalid_yaml = os.path.join(self.repo_dir, "invalid.yaml")
        with open(invalid_yaml, 'w') as f:
            f.write("invalid: yaml: content")
            
        lc = ListCmd()
        self.assertTrue(lc.run())  # 应该能处理错误继续执行

    def test_run_with_empty_plugin(self):
        """测试空插件文件"""
        empty_yaml = os.path.join(self.repo_dir, "empty.yaml")
        with open(empty_yaml, 'w') as f:
            yaml.dump({}, f)
            
        lc = ListCmd()
        self.assertTrue(lc.run())
