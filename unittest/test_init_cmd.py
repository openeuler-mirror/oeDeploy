# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.

import unittest
import os
import tempfile
import shutil
import tarfile
from unittest.mock import patch, MagicMock
import yaml

from src.commands.init.init_cmd import InitCmd
from src.constants.paths import PLUGIN_DIR, REPO_CACHE_DIR, REPO_CONFIG_PATH


class TestInitCmd(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试插件目录结构
        self.test_plugin_dir = os.path.join(self.temp_dir, "test_plugin")
        os.makedirs(self.test_plugin_dir)
        os.makedirs(os.path.join(self.test_plugin_dir, "workspace"))
        
        # 创建config.yaml文件
        self.config_content = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin for unit testing"
        }
        with open(os.path.join(self.test_plugin_dir, "config.yaml"), 'w') as f:
            yaml.dump(self.config_content, f)
        
        # 创建main.yaml文件
        self.main_content = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin for unit testing",
            "action": {
                "install": {"description": "Install the plugin"},
                "uninstall": {"description": "Uninstall the plugin"}
            }
        }
        with open(os.path.join(self.test_plugin_dir, "main.yaml"), 'w') as f:
            yaml.dump(self.main_content, f)
        
        # 创建压缩包
        self.tar_path = os.path.join(self.temp_dir, "test_plugin.tar.gz")
        with tarfile.open(self.tar_path, 'w:gz') as tar:
            tar.add(self.test_plugin_dir, arcname=os.path.basename(self.test_plugin_dir))
        
        # 创建目标目录
        self.target_dir = os.path.join(self.temp_dir, "target_project")

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        """测试InitCmd初始化"""
        init_cmd = InitCmd("test_plugin", self.target_dir)
        self.assertEqual(init_cmd.plugin, "test_plugin")
        self.assertEqual(init_cmd.project, self.target_dir)
        self.assertEqual(init_cmd.parent_dir, "")
        self.assertFalse(init_cmd.force)
        self.assertIsNotNone(init_cmd.log)

    def test_init_with_parent_dir(self):
        """测试InitCmd初始化（带父目录）"""
        parent_dir = "/parent/dir"
        init_cmd = InitCmd("test_plugin", "", parent_dir=parent_dir)
        self.assertEqual(init_cmd.plugin, "test_plugin")
        self.assertEqual(init_cmd.project, "")
        self.assertEqual(init_cmd.parent_dir, parent_dir)
        self.assertFalse(init_cmd.force)

    def test_init_with_force(self):
        """测试InitCmd初始化（强制模式）"""
        init_cmd = InitCmd("test_plugin", self.target_dir, force=True)
        self.assertTrue(init_cmd.force)

    def test_determine_target_path_with_project(self):
        """测试目标路径确定（指定项目路径）"""
        init_cmd = InitCmd("test_plugin", self.target_dir)
        result = init_cmd._determine_target_path()
        self.assertEqual(result, os.path.abspath(self.target_dir))

    def test_determine_target_path_with_parent_dir(self):
        """测试目标路径确定（指定父目录）"""
        parent_dir = self.temp_dir
        init_cmd = InitCmd("test_plugin", "", parent_dir=parent_dir)
        result = init_cmd._determine_target_path()
        expected = os.path.abspath(os.path.join(parent_dir, "test_plugin"))
        self.assertEqual(result, expected)

    def test_determine_target_path_with_tar_and_parent_dir(self):
        """测试目标路径确定（压缩包和父目录）"""
        parent_dir = self.temp_dir
        init_cmd = InitCmd(self.tar_path, "", parent_dir=parent_dir)
        result = init_cmd._determine_target_path()
        expected = os.path.abspath(os.path.join(parent_dir, "test_plugin"))
        self.assertEqual(result, expected)

    def test_determine_target_path_default(self):
        """测试目标路径确定（默认情况）"""
        init_cmd = InitCmd("test_plugin", "")
        result = init_cmd._determine_target_path()
        expected = os.path.abspath(os.path.join(os.getcwd(), "test_plugin"))
        self.assertEqual(result, expected)

    def test_validate_target_path_valid(self):
        """测试目标路径验证（有效路径）"""
        init_cmd = InitCmd("test_plugin", self.target_dir)
        result = init_cmd._validate_target_path("/valid/path/to/project")
        self.assertTrue(result)

    def test_validate_target_path_invalid(self):
        """测试目标路径验证（无效路径）"""
        init_cmd = InitCmd("test_plugin", self.target_dir)
        result = init_cmd._validate_target_path("/")
        self.assertFalse(result)

    def test_handle_existing_target_empty(self):
        """测试处理已存在目标（空目录）"""
        os.makedirs(self.target_dir)
        
        init_cmd = InitCmd("test_plugin", self.target_dir)
        result = init_cmd._handle_existing_target(self.target_dir)
        
        self.assertTrue(result)

    def test_handle_existing_target_non_empty_with_force(self):
        """测试处理已存在目标（非空目录，强制模式）"""
        os.makedirs(self.target_dir)
        with open(os.path.join(self.target_dir, "test.txt"), 'w') as f:
            f.write("test content")
        
        init_cmd = InitCmd("test_plugin", self.target_dir, force=True)
        
        with patch('src.commands.init.init_cmd.CommandExecutor') as mock_executor:
            mock_executor.run_single_cmd.return_value = ("", "", 0)
            result = init_cmd._handle_existing_target(self.target_dir)
            
            self.assertTrue(result)

    def test_handle_existing_target_non_empty_without_force(self):
        """测试处理已存在目标（非空目录，非强制模式）"""
        os.makedirs(self.target_dir)
        with open(os.path.join(self.target_dir, "test.txt"), 'w') as f:
            f.write("test content")
        
        init_cmd = InitCmd("test_plugin", self.target_dir, force=False)
        result = init_cmd._handle_existing_target(self.target_dir)
        
        self.assertFalse(result)

    def test_extract_archive_success(self):
        """测试解压压缩包（成功）"""
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        with patch('src.commands.init.init_cmd.CommandExecutor') as mock_executor:
            mock_executor.run_single_cmd.return_value = ("", "", 0)
            
            result = init_cmd._extract_archive(self.tar_path, self.target_dir)
            
            self.assertTrue(result)
            mock_executor.run_single_cmd.assert_called_once()

    def test_extract_archive_failure(self):
        """测试解压压缩包（失败）"""
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        with patch('src.commands.init.init_cmd.CommandExecutor') as mock_executor:
            mock_executor.run_single_cmd.return_value = ("", "extraction error", 1)
            
            result = init_cmd._extract_archive(self.tar_path, self.target_dir)
            
            self.assertFalse(result)

    def test_extract_archive_exception(self):
        """测试解压压缩包（异常）"""
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        with patch('src.commands.init.init_cmd.CommandExecutor') as mock_executor:
            mock_executor.run_single_cmd.side_effect = Exception("Unexpected error")
            
            result = init_cmd._extract_archive(self.tar_path, self.target_dir)
            
            self.assertFalse(result)

    @patch('src.commands.init.init_cmd.CommandExecutor')
    def test_run_with_local_tar(self, mock_executor):
        """测试运行（本地压缩包）"""
        mock_executor.run_single_cmd.return_value = ("", "", 0)
        
        init_cmd = InitCmd(self.tar_path, self.target_dir)
        result = init_cmd.run()
        
        self.assertTrue(result)

    @patch('src.commands.init.init_cmd.CommandExecutor')
    def test_run_with_url_tar(self, mock_executor):
        """测试运行（URL压缩包）"""
        mock_executor.run_single_cmd.return_value = ("", "", 0)
        
        init_cmd = InitCmd("http://example.com/test.tar.gz", self.target_dir)
        result = init_cmd.run()
        
        self.assertTrue(result)

    @patch('src.commands.init.init_cmd.CommandExecutor')
    def test_run_with_plugin_name(self, mock_executor):
        """测试运行（插件名称）"""
        # 创建仓库配置和缓存
        os.makedirs(REPO_CACHE_DIR, exist_ok=True)
        repo_config = {
            'plugins': [
                {
                    'test_plugin': [
                        {
                            'version': '1.0.0',
                            'urls': ['http://example.com/test_plugin.tar.gz'],
                            'sha256sum': 'test_checksum'
                        }
                    ]
                }
            ]
        }
        with open(os.path.join(REPO_CACHE_DIR, 'test_repo.yaml'), 'w') as f:
            yaml.dump(repo_config, f)
        
        # 创建插件缓存目录
        os.makedirs(PLUGIN_DIR, exist_ok=True)
        
        mock_executor.run_single_cmd.return_value = ("", "", 0)
        
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        with patch.object(init_cmd, '_verify_checksum', return_value=True):
            result = init_cmd.run()
            
            self.assertTrue(result)

    def test_verify_checksum_success(self):
        """测试校验和验证（成功）"""
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # 计算正确的校验和
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(test_file, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        expected_checksum = sha256_hash.hexdigest()
        
        result = init_cmd._verify_checksum(test_file, expected_checksum)
        self.assertTrue(result)

    def test_verify_checksum_failure(self):
        """测试校验和验证（失败）"""
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        result = init_cmd._verify_checksum(test_file, "invalid_checksum")
        self.assertFalse(result)

    def test_verify_checksum_exception(self):
        """测试校验和验证（异常）"""
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        result = init_cmd._verify_checksum("/invalid/path", "checksum")
        self.assertFalse(result)

    @patch('src.commands.init.init_cmd.CommandExecutor')
    def test_download_with_retry_success(self, mock_executor):
        """测试带重试下载（成功）"""
        mock_executor.run_single_cmd.return_value = ("", "", 0)
        
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        url = "http://example.com/file.tar.gz"
        output_file = os.path.join(self.temp_dir, "downloaded.tar.gz")
        
        result = init_cmd._download_with_retry(url, output_file, "test_repo")
        
        self.assertTrue(result)

    @patch('src.commands.init.init_cmd.CommandExecutor')
    def test_download_with_retry_failure(self, mock_executor):
        """测试带重试下载（失败）"""
        mock_executor.run_single_cmd.return_value = ("", "download error", 1)
        
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        url = "http://example.com/file.tar.gz"
        output_file = os.path.join(self.temp_dir, "downloaded.tar.gz")
        
        result = init_cmd._download_with_retry(url, output_file, "test_repo")
        
        self.assertFalse(result)

    def test_find_plugin_in_repos_success(self):
        """测试在仓库中查找插件（成功）"""
        # 创建仓库缓存
        os.makedirs(REPO_CACHE_DIR, exist_ok=True)
        repo_config = {
            'plugins': [
                {
                    'test_plugin': [
                        {
                            'version': '1.0.0',
                            'urls': ['http://example.com/test_plugin.tar.gz'],
                            'sha256sum': 'test_checksum'
                        }
                    ]
                }
            ]
        }
        with open(os.path.join(REPO_CACHE_DIR, 'test_repo.yaml'), 'w') as f:
            yaml.dump(repo_config, f)
        
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        with patch.object(init_cmd, '_update_repo', return_value=True):
            result = init_cmd._find_plugin_in_repos()
            
            self.assertIsNotNone(result)
            self.assertEqual(result['version'], '1.0.0')

    def test_find_plugin_in_repos_not_found(self):
        """测试在仓库中查找插件（未找到）"""
        # 创建仓库缓存（不包含目标插件）
        os.makedirs(REPO_CACHE_DIR, exist_ok=True)
        repo_config = {
            'plugins': [
                {
                    'other_plugin': [
                        {
                            'version': '1.0.0',
                            'urls': ['http://example.com/other_plugin.tar.gz'],
                            'sha256sum': 'test_checksum'
                        }
                    ]
                }
            ]
        }
        with open(os.path.join(REPO_CACHE_DIR, 'test_repo.yaml'), 'w') as f:
            yaml.dump(repo_config, f)
        
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        with patch.object(init_cmd, '_update_repo', return_value=True):
            result = init_cmd._find_plugin_in_repos()
            
            self.assertIsNone(result)

    def test_find_plugin_in_repos_update_failed(self):
        """测试在仓库中查找插件（更新失败）"""
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        with patch.object(init_cmd, '_update_repo', return_value=False):
            result = init_cmd._find_plugin_in_repos()
            
            self.assertIsNone(result)

    def test_exception_handling(self):
        """测试异常处理"""
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        with patch.object(init_cmd, '_determine_target_path') as mock_method:
            mock_method.side_effect = Exception("Test exception")
            
            result = init_cmd.run()
            
            self.assertFalse(result)

    @patch('src.commands.init.init_cmd.LoggerGenerator')
    def test_logger_initialization(self, mock_logger_generator):
        """测试日志生成器初始化"""
        mock_logger = MagicMock()
        mock_logger_generator.return_value.get_logger.return_value = mock_logger
        
        init_cmd = InitCmd("test_plugin", self.target_dir)
        
        mock_logger_generator.return_value.get_logger.assert_called_once_with('init_cmd')
        self.assertEqual(init_cmd.log, mock_logger)


if __name__ == '__main__':
    unittest.main()
