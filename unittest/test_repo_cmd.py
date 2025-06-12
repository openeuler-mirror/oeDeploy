# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.

import unittest
import os
import tempfile
import shutil
import configparser
from unittest.mock import patch, MagicMock
import src.constants.paths
from src.commands.repo.repo_cmd import RepoCmd
from src.constants.paths import REPO_CONFIG_PATH, REPO_CACHE_DIR

class TestRepoCmd(unittest.TestCase):
    def setUp(self):
        # 创建临时目录
        self.test_dir = tempfile.mkdtemp()
        self.repo_config = os.path.join(self.test_dir, "repo.conf")
        self.repo_cache = os.path.join(self.test_dir, "repo_cache")
        os.makedirs(self.repo_cache, exist_ok=True)
        
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
        
        # 使用patch模拟路径常量
        self.repo_config_patcher = patch('src.constants.paths.REPO_CONFIG_PATH', self.repo_config)
        self.repo_cache_patcher = patch('src.constants.paths.REPO_CACHE_DIR', self.repo_cache)
        
        self.repo_config_patcher.start()
        self.repo_cache_patcher.start()
        
        # 模拟命令行参数
        self.args = MagicMock()
        
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.test_dir)
        # 停止patch恢复原始路径
        self.repo_config_patcher.stop()
        self.repo_cache_patcher.stop()
    
    def test_run_list(self):
        """测试列出仓库"""
        self.args.subcommand = 'list'
        repo_cmd = RepoCmd(self.args)
        
        with patch('src.commands.repo.repo_cmd.RepoCmd._check_config_and_cache_dir', return_value=True), \
             patch('src.commands.repo.repo_cmd.RepoCmd._read_repo_config') as mock_read:
            mock_read.return_value = configparser.ConfigParser()
            mock_read.return_value.read(self.repo_config)
            
            result = repo_cmd.run()
            self.assertTrue(result)
    
    @patch('src.commands.repo.repo_cmd.RepoCmd._download_with_retry')
    @patch('src.commands.repo.repo_cmd.RepoCmd._read_repo_config')
    def test_run_update(self, mock_read_config, mock_download):
        """测试更新仓库"""
        # 创建mock配置
        mock_config = configparser.ConfigParser()
        mock_config.add_section('test_repo')
        mock_config.set('test_repo', 'enabled', 'true')
        mock_config.set('test_repo', 'url', 'http://example.com/repo')
        mock_read_config.return_value = mock_config
        
        self.args.subcommand = 'update'
        repo_cmd = RepoCmd(self.args)
    
        mock_download.return_value = True
        result = repo_cmd.run()
    
        self.assertTrue(result)
        mock_download.assert_called()
    
    @patch('src.commands.repo.repo_cmd.RepoCmd._download_repo_index')
    @patch('src.commands.repo.repo_cmd.configparser.ConfigParser')
    def test_run_set(self, mock_config, mock_download):
        """测试设置仓库"""
        mock_download.return_value = True
        mock_config_instance = mock_config.return_value
        mock_config_instance.has_section.return_value = False
    
        self.args.subcommand = 'set'
        self.args.name = 'test_repo'
        self.args.url = 'http://example.com/new'
        repo_cmd = RepoCmd(self.args)
    
        result = repo_cmd.run()
        self.assertTrue(result)
    
        # 验证配置操作
        mock_config_instance.add_section.assert_called_once_with('test_repo')
        mock_config_instance.set.assert_any_call('test_repo', 'enabled', 'true')
        mock_config_instance.set.assert_any_call('test_repo', 'url', 'http://example.com/new')
    
    @patch('src.commands.repo.repo_cmd.os.path.exists')
    @patch('src.commands.repo.repo_cmd.os.remove')
    @patch('src.commands.repo.repo_cmd.configparser.ConfigParser')
    def test_run_del(self, mock_config, mock_remove, mock_exists):
        """测试删除仓库"""
        # 设置mock返回值
        mock_exists.return_value = True
        mock_config_instance = mock_config.return_value
        mock_config_instance.has_section.return_value = True
    
        self.args.subcommand = 'del'
        self.args.name = 'test_repo'
        repo_cmd = RepoCmd(self.args)
    
        result = repo_cmd.run()
        self.assertTrue(result)
        
        # 验证操作
        mock_config_instance.remove_section.assert_called_once_with('test_repo')
        mock_remove.assert_called_once_with(os.path.join(REPO_CACHE_DIR, 'test_repo.yaml'))
    
    @patch('src.commands.repo.repo_cmd.configparser.ConfigParser')
    def test_run_enable(self, mock_config):
        """测试启用仓库"""
        mock_config_instance = mock_config.return_value
        mock_config_instance.has_section.return_value = True
        mock_config_instance.get.return_value = 'true'  # 模拟get方法返回
    
        self.args.subcommand = 'enable'
        self.args.name = 'test_repo'
        repo_cmd = RepoCmd(self.args)
    
        with patch('src.commands.repo.repo_cmd.RepoCmd._download_repo_index', return_value=True):
            result = repo_cmd.run()
            self.assertTrue(result)
            mock_config_instance.set.assert_called_once_with('test_repo', 'enabled', 'true')
    
    @patch('src.commands.repo.repo_cmd.configparser.ConfigParser')
    def test_run_disable(self, mock_config):
        """测试禁用仓库"""
        mock_config_instance = mock_config.return_value
        mock_config_instance.has_section.return_value = True
        mock_config_instance.get.return_value = 'false'  # 模拟get方法返回
    
        self.args.subcommand = 'disable'
        self.args.name = 'test_repo'
        repo_cmd = RepoCmd(self.args)
    
        with patch('src.commands.repo.repo_cmd.RepoCmd._remove_repo_cache', return_value=True):
            result = repo_cmd.run()
            self.assertTrue(result)
            mock_config_instance.set.assert_called_once_with('test_repo', 'enabled', 'false')
    
    @patch('src.commands.repo.repo_cmd.CommandExecutor.run_single_cmd')
    def test_download_with_retry(self, mock_cmd):
        """测试带重试的下载功能"""
        self.args.subcommand = 'update'
        repo_cmd = RepoCmd(self.args)
        
        # 第一次失败，第二次成功
        mock_cmd.side_effect = [
            ("", "error", 1),
            ("", "", 0)
        ]
        
        result = repo_cmd._download_with_retry(
            "http://example.com/index.yaml",
            os.path.join(self.repo_cache, "test.yaml"),
            "test_repo"
        )
        
        self.assertTrue(result)
        self.assertEqual(mock_cmd.call_count, 2)
    @patch('src.commands.repo.repo_cmd.os.remove')
    @patch('src.commands.repo.repo_cmd.os.listdir')
    def test_cleanup_old_cache_files(self, mock_listdir, mock_remove):
        """测试清理旧缓存文件"""
        self.args.subcommand = 'update'
        repo_cmd = RepoCmd(self.args)
    
        # 设置mock返回值
        mock_listdir.return_value = ['test_repo.yaml', 'old_repo.yaml']
        
        # 执行清理
        repo_cmd._cleanup_old_cache_files({os.path.join(REPO_CACHE_DIR, 'test_repo.yaml')})
        
        # 验证删除操作
        mock_remove.assert_called_once_with(os.path.join(REPO_CACHE_DIR, 'old_repo.yaml'))

    @patch('src.commands.repo.repo_cmd.CommandExecutor.run_single_cmd')
    def test_invalid_url_handling(self, mock_cmd):
        """测试无效URL的处理"""
        self.args.subcommand = 'update'
        repo_cmd = RepoCmd(self.args)
        
        # 模拟curl命令失败
        mock_cmd.return_value = ("", "Could not resolve host", 6)
        
        # 创建mock配置
        mock_config = configparser.ConfigParser()
        mock_config.add_section('invalid_repo')
        mock_config.set('invalid_repo', 'enabled', 'true')
        mock_config.set('invalid_repo', 'url', 'http://invalid.example.com')
        
        with patch('src.commands.repo.repo_cmd.RepoCmd._read_repo_config', return_value=mock_config):
            result = repo_cmd.run()
            
        self.assertFalse(result)  # 当前实现遇到无效URL返回False
        mock_cmd.assert_called()
    
    def test_missing_required_fields(self):
        """测试配置文件中缺少必要字段的情况"""
        self.args.subcommand = 'update'
        repo_cmd = RepoCmd(self.args)
        
        # 创建缺少必要字段的配置
        mock_config = configparser.ConfigParser()
        mock_config.add_section('incomplete_repo')
        mock_config.set('incomplete_repo', 'url', 'http://example.com')
        # 缺少enabled字段
        
        with patch('src.commands.repo.repo_cmd.RepoCmd._read_repo_config', return_value=mock_config):
            result = repo_cmd.run()
            
        self.assertFalse(result)  # 当前实现遇到无效配置返回False
    
    @patch('src.commands.repo.repo_cmd.os.path.exists')
    @patch('src.commands.repo.repo_cmd.os.remove')
    def test_permission_denied_scenarios(self, mock_remove, mock_exists):
        """测试权限不足的场景"""
        self.args.subcommand = 'update'
        repo_cmd = RepoCmd(self.args)
        
        # 模拟权限不足
        mock_remove.side_effect = PermissionError("Permission denied")
        mock_exists.return_value = True
        
        # 创建mock配置
        mock_config = configparser.ConfigParser()
        mock_config.add_section('test_repo')
        mock_config.set('test_repo', 'enabled', 'true')
        mock_config.set('test_repo', 'url', 'http://example.com/repo')
        
        with patch('src.commands.repo.repo_cmd.RepoCmd._read_repo_config', return_value=mock_config), \
             patch('src.commands.repo.repo_cmd.CommandExecutor.run_single_cmd', return_value=("", "", 0)):
            result = repo_cmd.run()
            
        self.assertTrue(result)  # 应该记录错误但继续执行
    
    @patch('src.commands.repo.repo_cmd.os.path.exists')
    @patch('src.commands.repo.repo_cmd.os.remove')
    @patch('src.commands.repo.repo_cmd.os.listdir')
    def test_concurrent_repo_operations(self, mock_listdir, mock_remove, mock_exists):
        """测试并发操作仓库配置"""
        self.args.subcommand = 'update'
        repo_cmd1 = RepoCmd(self.args)
        repo_cmd2 = RepoCmd(self.args)
        
        # 设置mock返回值
        mock_exists.return_value = True
        mock_listdir.return_value = ['test_repo.yaml']
        
        # 创建mock配置
        mock_config = configparser.ConfigParser()
        mock_config.add_section('test_repo')
        mock_config.set('test_repo', 'enabled', 'true')
        mock_config.set('test_repo', 'url', 'http://example.com/repo')
        
        with patch('src.commands.repo.repo_cmd.RepoCmd._read_repo_config', return_value=mock_config), \
             patch('src.commands.repo.repo_cmd.CommandExecutor.run_single_cmd', return_value=("", "", 0)):
            result1 = repo_cmd1.run()
            result2 = repo_cmd2.run()
            
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertEqual(mock_remove.call_count, 2)  # 每个实例调用一次
