# -*- coding: utf-8 -*-
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.

import unittest
import os
import tempfile
from unittest.mock import patch
from src.commands.list.list_cmd import ListCmd
from src.exceptions.config_exception import ConfigException

class TestListCmd(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.valid_plugin = os.path.join(self.test_dir.name, "test_plugin.tar.gz")
        open(self.valid_plugin, 'a').close()
        
    def tearDown(self):
        self.test_dir.cleanup()

    def test_run_with_invalid_source(self):
        """测试无效源目录"""
        lc = ListCmd("/non/existent/path")
        self.assertFalse(lc.run())

    def test_run_with_empty_source(self):
        """测试空插件目录"""
        lc = ListCmd(self.test_dir.name)
        self.assertTrue(lc.run())

    @patch('src.utils.main_reader.MainReader.get_name')
    @patch('src.utils.main_reader.MainReader.get_version')
    @patch('src.utils.main_reader.MainReader.get_description')
    def test_run_with_valid_plugin(self, mock_desc, mock_ver, mock_name):
        """测试有效插件解析"""
        mock_name.return_value = "TestPlugin"
        mock_ver.return_value = "1.0.0"
        mock_desc.return_value = "Test Description"
        
        lc = ListCmd(self.test_dir.name)
        self.assertTrue(lc.run())

    @patch('src.utils.main_reader.MainReader.get_name')
    def test_run_with_invalid_plugin(self, mock_name):
        """测试无效插件文件"""
        mock_name.side_effect = ConfigException("Invalid config")
        
        lc = ListCmd(self.test_dir.name)
        self.assertTrue(lc.run())

if __name__ == '__main__':
    unittest.main()
