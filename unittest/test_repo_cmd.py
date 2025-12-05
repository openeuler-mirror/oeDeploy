# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.

import unittest
import os
import tempfile
import shutil
import configparser
import tarfile
import yaml
from unittest.mock import patch, MagicMock
import src.constants.paths
from src.commands.repo.repo_cmd import RepoCmd
from src.constants.paths import REPO_CONFIG_PATH, REPO_CACHE_DIR, PLUGIN_DETAILS_DIR

class TestRepoCmd(unittest.TestCase):
    def setUp(self):
        # 创建临时目录
        self.test_dir = tempfile.mkdtemp()
        self.repo_config = os.path.join(self.test_dir, "repo.conf")
        self.repo_cache = os.path.join(self.test_dir, "repo_cache")
        self.plugin_details = os.path.join(self.test_dir, "details")
        os.makedirs(self.repo_cache, exist_ok=True)
        os.makedirs(self.plugin_details, exist_ok=True)
        
        # 创建测试repo配置
        with open(self.repo_config, 'w') as f:
            f.write("[test_repo]\nurl = http://example.com/repo\nenabled = true\n")
            f.write("[disabled_repo]\nurl = http://example.com/disabled\nenabled = false\n")
        
        # 创建测试缓存文件
        with open(os.path.join(self.repo_cache, "test_repo.yaml"), 'w') as f:
            f.write("plugins: []")
        
        # 备份原始路径常量
        self.original_repo_config = src.constants.paths.REPO_CONFIG_PATH
        self.original_repo_cache = src.constants.paths.REPO_CACHE_DIR
        self.original_plugin_details = src.constants.paths.PLUGIN_DETAILS_DIR
        
        # 使用patch模拟路径常量
        self.repo_config_patcher = patch('src.constants.paths.REPO_CONFIG_PATH', self.repo_config)
        self.repo_cache_patcher = patch('src.constants.paths.REPO_CACHE_DIR', self.repo_cache)
        self.plugin_details_patcher = patch('src.constants.paths.PLUGIN_DETAILS_DIR', self.plugin_details)
        
        self.repo_config_patcher.start()
        self.repo_cache_patcher.start()
        self.plugin_details_patcher.start()
        
        # 模拟命令行参数
        self.args = MagicMock()
        
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.test_dir)
        # 停止patch恢复原始路径
        self.repo_config_patcher.stop()
        self.repo_cache_patcher.stop()
        self.plugin_details_patcher.stop()
    
    def test_run_list(self):
        """测试列出仓库"""
        self.args.subcommand = 'list'
        repo_cmd = RepoCmd(self.args)
        result = repo_cmd.run()
        self.assertTrue(result)
    
    @patch('src.commands.repo.repo_cmd.RepoCmd._download_with_retry')
    def test_run_update(self, mock_download):
        """测试更新仓库"""
        mock_download.return_value = True
        self.args.subcommand = 'update'
        repo_cmd = RepoCmd(self.args)
        result = repo_cmd.run()
        self.assertTrue(result)
        mock_download.assert_called()
    
    @patch('src.commands.repo.repo_cmd.RepoCmd._download_repo_index')
    def test_run_set(self, mock_download):
        """测试设置仓库"""
        mock_download.return_value = True
        self.args.subcommand = 'set'
        self.args.name = 'new_repo'
        self.args.url = 'http://example.com/new'
        repo_cmd = RepoCmd(self.args)
        result = repo_cmd.run()
        self.assertTrue(result)
        mock_download.assert_called_once()
    
    @patch('src.commands.repo.repo_cmd.REPO_CONFIG_PATH')
    @patch('src.commands.repo.repo_cmd.REPO_CACHE_DIR')
    def test_run_del(self, mock_cache_dir, mock_config_path):
        """测试删除仓库"""
        mock_config_path.return_value = self.repo_config
        mock_cache_dir.return_value = self.repo_cache
        
        self.args.subcommand = 'del'
        self.args.name = 'test_repo'
        
        with patch('src.commands.repo.repo_cmd.RepoCmd._read_repo_config') as mock_read:
            config = configparser.ConfigParser()
            config.read(self.repo_config)
            mock_read.return_value = config
            
            with patch('src.commands.repo.repo_cmd.RepoCmd._remove_repo_cache', return_value=True):
                repo_cmd = RepoCmd(self.args)
                result = repo_cmd.run()
                self.assertTrue(result)
    
    @patch('src.commands.repo.repo_cmd.RepoCmd._download_repo_index')
    def test_run_enable(self, mock_download):
        """测试启用仓库"""
        mock_download.return_value = True
        self.args.subcommand = 'enable'
        self.args.name = 'disabled_repo'
        
        with patch('src.commands.repo.repo_cmd.RepoCmd._read_repo_config') as mock_read:
            config = configparser.ConfigParser()
            config.read(self.repo_config)
            mock_read.return_value = config
            
            repo_cmd = RepoCmd(self.args)
            result = repo_cmd.run()
            self.assertTrue(result)
            mock_download.assert_called_once()
    
    def test_run_disable(self):
        """测试禁用仓库"""
        self.args.subcommand = 'disable'
        self.args.name = 'test_repo'
        
        with patch('src.commands.repo.repo_cmd.RepoCmd._read_repo_config') as mock_read:
            config = configparser.ConfigParser()
            config.read(self.repo_config)
            mock_read.return_value = config
            
            with patch('src.commands.repo.repo_cmd.RepoCmd._remove_repo_cache', return_value=True):
                repo_cmd = RepoCmd(self.args)
                result = repo_cmd.run()
                self.assertTrue(result)
    
    @patch('src.commands.repo.repo_cmd.CommandExecutor.run_single_cmd')
    def test_download_with_retry_success(self, mock_cmd):
        """测试带重试的下载功能成功"""
        self.args.subcommand = 'update'
        repo_cmd = RepoCmd(self.args)
        mock_cmd.return_value = ("", "", 0)
        
        result = repo_cmd._download_with_retry(
            "http://example.com/index.yaml",
            os.path.join(self.repo_cache, "test.yaml"),
            "test_repo"
        )
        
        self.assertTrue(result)
        mock_cmd.assert_called_once()
    
    @patch('src.commands.repo.repo_cmd.CommandExecutor.run_single_cmd')
    def test_download_with_retry_failure(self, mock_cmd):
        """测试带重试的下载功能失败"""
        self.args.subcommand = 'update'
        repo_cmd = RepoCmd(self.args)
        mock_cmd.return_value = ("", "error", 1)
        
        result = repo_cmd._download_with_retry(
            "http://example.com/index.yaml",
            os.path.join(self.repo_cache, "test.yaml"),
            "test_repo",
            max_retries=2
        )
        
        self.assertFalse(result)
        self.assertEqual(mock_cmd.call_count, 2)
    
    def test_cleanup_old_cache_files(self):
        """测试清理旧缓存文件"""
        self.args.subcommand = 'update'
        
        # 创建一些测试文件
        old_file = os.path.join(self.repo_cache, 'old_repo.yaml')
        with open(old_file, 'w') as f:
            f.write("plugins: []")
        
        keep_file = os.path.join(self.repo_cache, 'keep_repo.yaml')
        with open(keep_file, 'w') as f:
            f.write("plugins: []")
        
        # 使用patch确保使用临时目录
        with patch('src.commands.repo.repo_cmd.REPO_CACHE_DIR', self.repo_cache):
            repo_cmd = RepoCmd(self.args)
            # 执行清理，保留keep_file
            repo_cmd._cleanup_old_cache_files({keep_file})
        
        # 验证
        self.assertFalse(os.path.exists(old_file))
        self.assertTrue(os.path.exists(keep_file))

    @patch('src.commands.repo.repo_cmd.CommandExecutor.run_single_cmd')
    def test_invalid_url_handling(self, mock_cmd):
        """测试无效URL的处理"""
        self.args.subcommand = 'update'
        repo_cmd = RepoCmd(self.args)
        mock_cmd.return_value = ("", "Could not resolve host", 6)
        result = repo_cmd.run()
        self.assertFalse(result)
    
    def test_missing_required_fields(self):
        """测试配置文件中缺少必要字段的情况"""
        # 创建只包含缺少enabled字段的repo的配置
        test_config = os.path.join(self.test_dir, "incomplete.conf")
        with open(test_config, 'w') as f:
            f.write("[incomplete_repo]\nurl = http://example.com\n")
        
        self.args.subcommand = 'update'
        
        with patch('src.commands.repo.repo_cmd.REPO_CONFIG_PATH', test_config):
            repo_cmd = RepoCmd(self.args)
            # 没有enabled字段的repo不会被处理，所以没有下载任何文件，返回False
            # 但也不会抛出异常
            result = repo_cmd.run()
            # 由于没有启用的repo，downloaded_files为空，返回False
            self.assertFalse(result)
    
    def test_del_nonexistent_repo(self):
        """测试删除不存在的仓库"""
        self.args.subcommand = 'del'
        self.args.name = 'nonexistent'
        repo_cmd = RepoCmd(self.args)
        result = repo_cmd.run()
        self.assertFalse(result)
    
    def test_enable_nonexistent_repo(self):
        """测试启用不存在的仓库"""
        self.args.subcommand = 'enable'
        self.args.name = 'nonexistent'
        repo_cmd = RepoCmd(self.args)
        result = repo_cmd.run()
        self.assertFalse(result)
    
    def test_disable_nonexistent_repo(self):
        """测试禁用不存在的仓库"""
        self.args.subcommand = 'disable'
        self.args.name = 'nonexistent'
        repo_cmd = RepoCmd(self.args)
        result = repo_cmd.run()
        self.assertFalse(result)
    
    def test_run_make(self):
        """测试生成插件源索引文件"""
        # 创建测试插件目录
        plugins_dir = os.path.join(self.test_dir, "plugins")
        os.makedirs(plugins_dir)
        
        # 创建一个模拟的插件tar.gz文件
        plugin_name = "test_plugin"
        plugin_dir = os.path.join(self.test_dir, "temp", plugin_name)
        os.makedirs(plugin_dir)
        
        # 创建main.yaml
        main_yaml = os.path.join(plugin_dir, "main.yaml")
        with open(main_yaml, 'w') as f:
            yaml.dump({
                "name": plugin_name,
                "version": "1.0.0",
                "description": "Test plugin",
                "type": "app",
                "localhost_available": True
            }, f)
        
        # 创建config.yaml
        config_yaml = os.path.join(plugin_dir, "config.yaml")
        with open(config_yaml, 'w') as f:
            f.write("test: config")
        
        # 创建workspace目录
        workspace_dir = os.path.join(plugin_dir, "workspace")
        os.makedirs(workspace_dir)
        
        # 打包成tar.gz
        tar_path = os.path.join(plugins_dir, f"{plugin_name}.tar.gz")
        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(plugin_dir, arcname=plugin_name)
        
        # 执行make命令
        self.args.subcommand = 'make'
        self.args.plugins_dir = plugins_dir
        self.args.url_prefix = 'http://example.com/plugins'
        self.args.output_dir = plugins_dir
        self.args.extra_item = ''
        
        repo_cmd = RepoCmd(self.args)
        result = repo_cmd.run()
        
        self.assertTrue(result)
        # 验证index.yaml文件被创建
        index_file = os.path.join(plugins_dir, 'index.yaml')
        self.assertTrue(os.path.exists(index_file))
        
        # 验证index.yaml内容
        with open(index_file, 'r') as f:
            index_data = yaml.safe_load(f)
            self.assertIn('plugins', index_data)
            self.assertEqual(index_data['apiversion'], 'v1')
    
    def test_run_make_local(self):
        """测试生成本地插件源索引文件"""
        # 创建测试插件目录
        plugins_dir = os.path.join(self.test_dir, "local_plugins")
        os.makedirs(plugins_dir)
        
        # 创建一个模拟的插件tar.gz文件
        plugin_name = "local_plugin"
        plugin_dir = os.path.join(self.test_dir, "temp2", plugin_name)
        os.makedirs(plugin_dir)
        
        # 创建main.yaml
        main_yaml = os.path.join(plugin_dir, "main.yaml")
        with open(main_yaml, 'w') as f:
            yaml.dump({
                "name": plugin_name,
                "version": "1.0.0",
                "description": "Local test plugin",
                "type": "app",
                "localhost_available": True
            }, f)
        
        # 创建config.yaml
        config_yaml = os.path.join(plugin_dir, "config.yaml")
        with open(config_yaml, 'w') as f:
            f.write("test: config")
        
        # 创建workspace目录
        workspace_dir = os.path.join(plugin_dir, "workspace")
        os.makedirs(workspace_dir)
        
        # 打包成tar.gz
        tar_path = os.path.join(plugins_dir, f"{plugin_name}.tar.gz")
        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(plugin_dir, arcname=plugin_name)
        
        # 执行make-local命令
        self.args.subcommand = 'make-local'
        self.args.path = plugins_dir
        
        repo_cmd = RepoCmd(self.args)
        result = repo_cmd.run()
        
        self.assertTrue(result)
        # 验证index.yaml文件被创建
        index_file = os.path.join(plugins_dir, 'index.yaml')
        self.assertTrue(os.path.exists(index_file))
        
        # 验证URL前缀（file://或绝对路径）
        with open(index_file, 'r') as f:
            index_data = yaml.safe_load(f)
            plugins = index_data['plugins']
            has_plugins = False
            for plugin_entry in plugins:
                for plugin_name, versions in plugin_entry.items():
                    for version_info in versions:
                        has_plugins = True
                        for url in version_info['urls']:
                            # URL格式是file:/path（单斜杠）
                            self.assertTrue(url.startswith('file:/'))
            self.assertTrue(has_plugins)
    
    def test_validate_and_extract_plugin_info_invalid(self):
        """测试验证无效插件"""
        # 创建一个无效的tar.gz文件
        invalid_tar = os.path.join(self.test_dir, "invalid.tar.gz")
        with tarfile.open(invalid_tar, 'w:gz') as tar:
            pass  # 空tar文件
        
        repo_cmd = RepoCmd(self.args)
        valid, info = repo_cmd._validate_and_extract_plugin_info(invalid_tar)
        self.assertFalse(valid)
        self.assertIsNone(info)
    
    def test_calculate_sha256(self):
        """测试计算文件sha256值"""
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        repo_cmd = RepoCmd(self.args)
        sha256 = repo_cmd._calculate_sha256(test_file)
        self.assertIsNotNone(sha256)
        self.assertEqual(len(sha256), 64)  # SHA256 hash is 64 hex chars
    
    def test_build_plugin_entry(self):
        """测试构建插件条目"""
        # 创建测试文件
        test_file = os.path.join(self.test_dir, "test_plugin.tar.gz")
        with open(test_file, 'wb') as f:
            f.write(b"test data")
        
        plugin_info = {
            'name': 'test_plugin',
            'version': '1.0.0',
            'updated': '',
            'author': 'test',
            'url': 'http://test.com',
            'description': 'test',
            'description_zh': '',
            'description_en': '',
            'readme': '',
            'icon': '',
            'type': 'app',
            'localhost_available': True
        }
        
        repo_cmd = RepoCmd(self.args)
        entry = repo_cmd._build_plugin_entry(test_file, self.test_dir, 'http://example.com', plugin_info)
        
        self.assertEqual(entry['name'], 'test_plugin')
        self.assertEqual(entry['version'], '1.0.0')
        self.assertIn('sha256sum', entry)
        self.assertIn('size', entry)
        self.assertIn('urls', entry)
    
    def test_check_config_and_cache_dir_missing_config(self):
        """测试配置文件不存在（list命令会读取实际的配置文件，即使patch了路径）"""
        # 由于list命令直接读取配置文件，patch可能不生效
        # 这个测试需要调整
        with patch('src.commands.repo.repo_cmd.REPO_CONFIG_PATH', '/nonexistent/repo.conf'):
            self.args.subcommand = 'list'
            repo_cmd = RepoCmd(self.args)
            result = repo_cmd.run()
            self.assertFalse(result)
    
    def test_check_config_and_cache_dir_missing_cache(self):
        """测试缓存目录不存在（list命令会使用实际的缓存目录）"""
        with patch('src.commands.repo.repo_cmd.REPO_CACHE_DIR', '/nonexistent/cache'):
            self.args.subcommand = 'list'
            repo_cmd = RepoCmd(self.args)
            result = repo_cmd.run()
            self.assertFalse(result)
