# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.

import unittest
import os
import tempfile
import shutil
import hashlib
from unittest.mock import patch, MagicMock
import src.constants.paths
from src.commands.init.init_cmd import InitCmd
from src.constants.paths import PLUGIN_DIR, REPO_CACHE_DIR, REPO_CONFIG_PATH

class TestInitCmd(unittest.TestCase):
    def setUp(self):
        # 创建临时目录
        self.test_dir = tempfile.mkdtemp()
        self.plugin_dir = os.path.join(self.test_dir, "plugin")
        os.makedirs(self.plugin_dir, exist_ok=True)
        
        # 创建测试插件压缩包
        self.test_plugin = os.path.join(self.plugin_dir, "test_plugin.tar.gz")
        with open(self.test_plugin, 'wb') as f:
            f.write(b'test data')
        
        # 备份原始路径常量
        self.original_plugin_dir = src.constants.paths.PLUGIN_DIR
        
        # 使用patch模拟路径常量
        self.plugin_patcher = patch('src.constants.paths.PLUGIN_DIR', self.plugin_dir)
        self.plugin_patcher.start()
        
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.test_dir)
        # 停止patch恢复原始路径
        self.plugin_patcher.stop()
    
    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_init_with_local_archive(self, mock_cmd):
        """测试使用本地压缩包初始化项目"""
        mock_cmd.return_value = ("", "", 0)
        
        target_path = os.path.join(self.test_dir, "new_project")
        init_cmd = InitCmd(self.test_plugin, target_path)
        result = init_cmd.run()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(target_path))
        mock_cmd.assert_called_once()
    
    @patch('src.commands.init.init_cmd.InitCmd._download_with_retry')
    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_init_with_remote_archive(self, mock_extract, mock_download):
        """测试使用远程URL初始化项目"""
        mock_download.return_value = True
        mock_extract.return_value = ("", "", 0)
        
        target_path = os.path.join(self.test_dir, "remote_project")
        init_cmd = InitCmd("http://example.com/plugin.tar.gz", target_path)
        result = init_cmd.run()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(target_path))
        mock_download.assert_called_once()
    
    @patch('src.commands.init.init_cmd.InitCmd._find_plugin_in_repos')
    def test_init_with_plugin_name(self, mock_find):
        """测试使用插件名称初始化项目"""
        mock_find.return_value = {
            'urls': ['http://example.com/plugin.tar.gz'],
            'sha256sum': '123456',
            'version': '1.0.0'
        }
        
        target_path = os.path.join(self.test_dir, "named_project")
        init_cmd = InitCmd("test_plugin", target_path)
        
        with patch('src.commands.init.init_cmd.InitCmd._download_with_retry', return_value=True), \
             patch('src.commands.init.init_cmd.InitCmd._verify_checksum', return_value=True), \
             patch('src.commands.init.init_cmd.InitCmd._extract_archive', return_value=True):
            result = init_cmd.run()
        
        self.assertTrue(result)
        mock_find.assert_called_once()
    
    def test_init_with_invalid_path(self):
        """测试使用无效路径初始化项目（路径层级小于2）"""
        init_cmd = InitCmd(self.test_plugin, "/tmp")
        result = init_cmd.run()
        
        self.assertFalse(result)
    
    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_init_with_existing_dir(self, mock_cmd):
        """测试目标目录已存在的情况"""
        mock_cmd.return_value = ("", "", 0)
        
        target_path = os.path.join(self.test_dir, "existing_project")
        os.makedirs(target_path)
        
        # 创建测试文件使目录非空
        with open(os.path.join(target_path, "testfile"), 'w') as f:
            f.write("test")
        
        # 测试不强制覆盖
        init_cmd = InitCmd(self.test_plugin, target_path, force=False)
        result = init_cmd.run()
        self.assertFalse(result)
        
        # 测试强制覆盖
        init_cmd = InitCmd(self.test_plugin, target_path, force=True)
        result = init_cmd.run()
        self.assertTrue(result)
    
    @patch('src.commands.init.init_cmd.InitCmd._find_plugin_in_repos')
    def test_init_with_missing_plugin(self, mock_find):
        """测试插件不存在的情况"""
        mock_find.return_value = None
        
        target_path = os.path.join(self.test_dir, "missing_plugin")
        init_cmd = InitCmd("nonexistent_plugin", target_path)
        result = init_cmd.run()
        
        self.assertFalse(result)

    @patch('src.commands.init.init_cmd.InitCmd._verify_checksum')
    def test_init_with_checksum_failure(self, mock_verify):
        """测试校验和验证失败的情况"""
        mock_verify.return_value = False
        
        target_path = os.path.join(self.test_dir, "checksum_fail")
        init_cmd = InitCmd("test_plugin", target_path)
        
        with patch('src.commands.init.init_cmd.InitCmd._find_plugin_in_repos') as mock_find:
            mock_find.return_value = {
                'urls': ['http://example.com/plugin.tar.gz'],
                'sha256sum': '123456',
                'version': '1.0.0'
            }
            with patch('src.commands.init.init_cmd.InitCmd._download_with_retry', return_value=True):
                result = init_cmd.run()
        
        self.assertFalse(result)

    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_extract_failure(self, mock_cmd):
        """测试解压失败处理"""
        mock_cmd.return_value = ("", "extract error", 1)
        
        target_path = os.path.join(self.test_dir, "extract_fail")
        init_cmd = InitCmd(self.test_plugin, target_path)
        result = init_cmd.run()
        
        self.assertFalse(result)

    @patch('src.commands.init.init_cmd.os.makedirs')
    def test_permission_denied(self, mock_makedirs):
        """测试文件权限不足"""
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        target_path = os.path.join(self.test_dir, "permission_test")
        init_cmd = InitCmd("http://example.com/plugin.tar.gz", target_path)
        result = init_cmd.run()
        
        self.assertFalse(result)

    def test_determine_target_path_with_project(self):
        """测试确定目标路径（指定project）"""
        init_cmd = InitCmd("test_plugin.tar.gz", "/opt/my_project")
        target = init_cmd._determine_target_path()
        self.assertEqual(target, os.path.abspath("/opt/my_project"))
    
    def test_determine_target_path_with_parent_dir(self):
        """测试确定目标路径（指定parent_dir）"""
        init_cmd = InitCmd("test_plugin.tar.gz", "", parent_dir="/opt")
        target = init_cmd._determine_target_path()
        self.assertEqual(target, os.path.abspath("/opt/test_plugin"))
    
    def test_determine_target_path_default(self):
        """测试确定目标路径（使用当前目录）"""
        init_cmd = InitCmd("test_plugin.tar.gz", "")
        target = init_cmd._determine_target_path()
        expected = os.path.abspath(os.path.join(os.getcwd(), "test_plugin"))
        self.assertEqual(target, expected)
    
    def test_verify_checksum_success(self):
        """测试校验和验证成功"""
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'wb') as f:
            f.write(b"test content")
        
        # 计算实际的checksum
        sha256_hash = hashlib.sha256()
        with open(test_file, 'rb') as f:
            sha256_hash.update(f.read())
        expected_checksum = sha256_hash.hexdigest()
        
        init_cmd = InitCmd("test", "/opt/test")
        result = init_cmd._verify_checksum(test_file, expected_checksum)
        self.assertTrue(result)
    
    def test_verify_checksum_failure(self):
        """测试校验和验证失败"""
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'wb') as f:
            f.write(b"test content")
        
        init_cmd = InitCmd("test", "/opt/test")
        result = init_cmd._verify_checksum(test_file, "wrong_checksum")
        self.assertFalse(result)
    
    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_download_with_retry_success(self, mock_cmd):
        """测试下载重试成功"""
        mock_cmd.return_value = ("", "", 0)
        
        init_cmd = InitCmd("test", "/opt/test")
        output_file = os.path.join(self.test_dir, "download.tar.gz")
        result = init_cmd._download_with_retry("http://example.com/test.tar.gz", output_file, "test")
        
        self.assertTrue(result)
        mock_cmd.assert_called_once()
    
    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_download_with_retry_failure(self, mock_cmd):
        """测试下载重试失败"""
        mock_cmd.return_value = ("", "error", 1)
        
        init_cmd = InitCmd("test", "/opt/test")
        output_file = os.path.join(self.test_dir, "download.tar.gz")
        result = init_cmd._download_with_retry("http://example.com/test.tar.gz", output_file, "test", max_retries=2)
        
        self.assertFalse(result)
        self.assertEqual(mock_cmd.call_count, 2)
    
    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_update_repo_success(self, mock_cmd):
        """测试更新仓库成功"""
        mock_cmd.return_value = ("", "", 0)
        
        init_cmd = InitCmd("test", "/opt/test")
        result = init_cmd._update_repo()
        
        self.assertTrue(result)
    
    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_update_repo_failure(self, mock_cmd):
        """测试更新仓库失败"""
        mock_cmd.return_value = ("", "error", 1)
        
        init_cmd = InitCmd("test", "/opt/test")
        result = init_cmd._update_repo()
        
        self.assertFalse(result)
    
    @patch('src.commands.init.init_cmd.InitCmd._update_repo')
    def test_find_plugin_update_failed(self, mock_update):
        """测试查找插件时更新仓库失败"""
        mock_update.return_value = False
        
        init_cmd = InitCmd("test_plugin", "/opt/test")
        result = init_cmd._find_plugin_in_repos()
        
        self.assertIsNone(result)
    
    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_extract_with_strip_components(self, mock_cmd):
        """测试解压时使用--strip-components=1参数"""
        mock_cmd.return_value = ("", "", 0)
        
        init_cmd = InitCmd("test", "/opt/test")
        target_path = os.path.join(self.test_dir, "extract_test")
        os.makedirs(target_path)
        
        result = init_cmd._extract_archive(self.test_plugin, target_path)
        
        self.assertTrue(result)
        args, _ = mock_cmd.call_args
        cmd = args[0]
        self.assertIn('--strip-components=1', cmd)
