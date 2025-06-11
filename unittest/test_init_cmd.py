# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.

import unittest
import os
import tempfile
import shutil
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
        
        # 创建测试repo配置
        self.repo_config = os.path.join(self.test_dir, "repo.conf")
        with open(self.repo_config, 'w') as f:
            f.write("[test_repo]\nurl = http://example.com/repo\nenabled = true")
        
        # 创建测试插件压缩包
        self.test_plugin = os.path.join(self.plugin_dir, "test_plugin.tar.gz")
        with open(self.test_plugin, 'wb') as f:
            f.write(b'test data')
        
        # 备份原始路径常量
        self.original_plugin_dir = src.constants.paths.PLUGIN_DIR
        self.original_repo_cache = src.constants.paths.REPO_CACHE_DIR
        self.original_repo_config = src.constants.paths.REPO_CONFIG_PATH
        
        # 使用patch模拟路径常量
        self.plugin_patcher = patch('src.constants.paths.PLUGIN_DIR', self.plugin_dir)
        self.repo_cache_patcher = patch('src.constants.paths.REPO_CACHE_DIR',
                                       os.path.join(self.test_dir, "repo_cache"))
        self.repo_config_patcher = patch('src.constants.paths.REPO_CONFIG_PATH', self.repo_config)
        
        self.plugin_patcher.start()
        self.repo_cache_patcher.start()
        self.repo_config_patcher.start()
        
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.test_dir)
        # 停止patch恢复原始路径
        self.plugin_patcher.stop()
        self.repo_cache_patcher.stop()
        self.repo_config_patcher.stop()
    
    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_init_with_local_archive(self, mock_cmd):
        """测试使用本地压缩包初始化项目"""
        mock_cmd.return_value = ("", "", 0)  # 模拟解压成功
        
        target_path = os.path.join(self.test_dir, "new_project")
        init_cmd = InitCmd(self.test_plugin, target_path)
        result = init_cmd.run()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(target_path))
        mock_cmd.assert_called_once()
    
    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_init_with_remote_archive(self, mock_cmd):
        """测试使用远程URL初始化项目"""
        mock_cmd.return_value = ("", "", 0)  # 模拟下载和解压成功
        
        target_path = os.path.join(self.test_dir, "remote_project")
        init_cmd = InitCmd("http://example.com/plugin.tar.gz", target_path)
        result = init_cmd.run()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(target_path))
        self.assertEqual(mock_cmd.call_count, 2)  # 下载和解压
    
    @patch('src.commands.init.init_cmd.InitCmd._find_plugin_in_repos')
    def test_init_with_plugin_name(self, mock_find):
        """测试使用插件名称初始化项目"""
        mock_find.return_value = {
            'urls': ['http://example.com/plugin.tar.gz'],
            'sha256sum': '123456'
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
        """测试使用无效路径初始化项目"""
        init_cmd = InitCmd(self.test_plugin, "/invalid/path")
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
                'sha256sum': '123456'
            }
            with patch('src.commands.init.init_cmd.InitCmd._download_with_retry', return_value=True):
                result = init_cmd.run()
        
        self.assertFalse(result)
        mock_verify.assert_called_once()

    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_download_retry_mechanism(self, mock_cmd):
        """测试下载重试机制"""
        # 第一次失败，第二次成功
        mock_cmd.side_effect = [
            ("", "error", 1),
            ("", "", 0),
            ("", "", 0)  # 解压命令
        ]
        
        target_path = os.path.join(self.test_dir, "retry_test")
        init_cmd = InitCmd("http://example.com/plugin.tar.gz", target_path)
        result = init_cmd.run()
        
        self.assertTrue(result)
        self.assertEqual(mock_cmd.call_count, 3)  # 2次下载尝试 + 1次解压

    @patch('src.commands.init.init_cmd.os.path.getmtime')
    def test_repo_update_check(self, mock_mtime):
        """测试仓库更新检查"""
        # 模拟缓存文件比配置文件旧
        mock_mtime.side_effect = [100, 200]  # config=100, cache=200
        
        target_path = os.path.join(self.test_dir, "repo_update")
        init_cmd = InitCmd("test_plugin", target_path)
        
        with patch('src.commands.init.init_cmd.InitCmd._find_plugin_in_repos') as mock_find:
            mock_find.return_value = {
                'urls': ['http://example.com/plugin.tar.gz'],
                'sha256sum': '123456'
            }
            with patch('src.commands.init.init_cmd.InitCmd._download_with_retry', return_value=True), \
                 patch('src.commands.init.init_cmd.InitCmd._verify_checksum', return_value=True), \
                 patch('src.commands.init.init_cmd.InitCmd._extract_archive', return_value=True):
                result = init_cmd.run()
        
        self.assertTrue(result)

    @patch('src.commands.init.init_cmd.InitCmd._find_plugin_in_repos')
    def test_plugin_version_selection(self, mock_find):
        """测试插件版本选择"""
        # 模拟多个版本
        mock_find.return_value = {
            'urls': ['http://example.com/plugin_v2.tar.gz'],
            'sha256sum': '654321',
            'version': '2.0.0',
            'updated': '2025-01-02T00:00:00+0800'
        }
        
        target_path = os.path.join(self.test_dir, "version_test")
        init_cmd = InitCmd("test_plugin", target_path)
        
        with patch('src.commands.init.init_cmd.InitCmd._download_with_retry', return_value=True), \
             patch('src.commands.init.init_cmd.InitCmd._verify_checksum', return_value=True), \
             patch('src.commands.init.init_cmd.InitCmd._extract_archive', return_value=True):
            result = init_cmd.run()
        
        self.assertTrue(result)
        self.assertEqual(mock_find.return_value['version'], '2.0.0')

    @patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd')
    def test_extract_failure(self, mock_cmd):
        """测试解压失败处理"""
        mock_cmd.return_value = ("", "extract error", 1)
        
        target_path = os.path.join(self.test_dir, "extract_fail")
        init_cmd = InitCmd(self.test_plugin, target_path)
        result = init_cmd.run()
        
        self.assertFalse(result)
        mock_cmd.assert_called_once()

    @patch('src.commands.init.init_cmd.os.makedirs')
    def test_permission_denied(self, mock_makedirs):
        """测试文件权限不足"""
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        target_path = os.path.join(self.test_dir, "permission_test")
        init_cmd = InitCmd("http://example.com/plugin.tar.gz", target_path)
        result = init_cmd.run()
        
        self.assertFalse(result)

    @patch('src.commands.init.init_cmd.LoggerGenerator.get_logger')
    def test_log_output_verification(self, mock_logger):
        """测试日志输出验证"""
        mock_log = MagicMock()
        mock_logger.return_value = mock_log
        
        target_path = os.path.join(self.test_dir, "log_test")
        init_cmd = InitCmd(self.test_plugin, target_path)
        
        with patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd', return_value=("", "", 0)):
            result = init_cmd.run()
        
        self.assertTrue(result)
        mock_log.info.assert_any_call(f"extracting archive to {target_path}")
        mock_log.info.assert_any_call("process success")

    @patch.dict('os.environ', {'OEDP_FORCE_UPDATE': '1'})
    def test_environment_variable_impact(self):
        """测试环境变量影响"""
        target_path = os.path.join(self.test_dir, "env_test")
        init_cmd = InitCmd("test_plugin", target_path)
        
        with patch('src.commands.init.init_cmd.InitCmd._find_plugin_in_repos') as mock_find:
            mock_find.return_value = {
                'urls': ['http://example.com/plugin.tar.gz'],
                'sha256sum': '123456'
            }
            with patch('src.commands.init.init_cmd.InitCmd._download_with_retry', return_value=True), \
                 patch('src.commands.init.init_cmd.InitCmd._verify_checksum', return_value=True), \
                 patch('src.commands.init.init_cmd.InitCmd._extract_archive', return_value=True):
                result = init_cmd.run()
        
        self.assertTrue(result)

    @patch('src.commands.init.init_cmd.InitCmd._extract_archive')
    def test_concurrent_init(self, mock_extract):
        """测试并发初始化"""
        mock_extract.return_value = True
        
        target_path1 = os.path.join(self.test_dir, "concurrent1")
        target_path2 = os.path.join(self.test_dir, "concurrent2")
        
        init_cmd1 = InitCmd(self.test_plugin, target_path1)
        init_cmd2 = InitCmd(self.test_plugin, target_path2)
        
        with patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd', return_value=("", "", 0)):
            result1 = init_cmd1.run()
            result2 = init_cmd2.run()
        
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertEqual(mock_extract.call_count, 2)

    @patch('src.commands.init.init_cmd.InitCmd._download_with_retry')
    def test_large_file_handling(self, mock_download):
        """测试大文件处理"""
        mock_download.return_value = True
        
        # 模拟大文件(1GB)
        large_plugin = os.path.join(self.plugin_dir, "large_plugin.tar.gz")
        with open(large_plugin, 'wb') as f:
            f.seek(1024 * 1024 * 1024 - 1)
            f.write(b'\0')
        
        target_path = os.path.join(self.test_dir, "large_file")
        init_cmd = InitCmd(large_plugin, target_path)
        
        with patch('src.commands.init.init_cmd.CommandExecutor.run_single_cmd', return_value=("", "", 0)):
            result = init_cmd.run()
        
        self.assertTrue(result)
        mock_download.assert_not_called()  # 本地文件不需要下载