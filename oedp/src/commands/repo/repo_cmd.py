# -*- coding: utf-8 -*-
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2025-04-19
# ======================================================================================================================

import configparser
import os
import shutil
import tarfile
import tempfile
from prettytable import PrettyTable
from typing import Set
from src.utils.command.command_executor import CommandExecutor
from src.utils.log.logger_generator import LoggerGenerator
from src.constants.paths import REPO_CONFIG_PATH, REPO_CACHE_DIR, PLUGIN_DETAILS_DIR

class RepoCmd:
    """插件源管理命令处理器"""
    
    def __init__(self, args):
        """初始化RepoCmd
        
        Args:
            args: 命令行参数对象
        """
        self.args = args
        self.log = LoggerGenerator().get_logger('repo_cmd')
        
    def run(self) -> bool:
        """执行repo子命令
        
        Returns:
            bool: 命令执行结果，成功返回True，失败返回False
        """
        command_map = {
            'list': self.run_list,
            'update': self.run_update,
            'set': self.run_set,
            'del': self.run_del,
            'enable': self.run_enable,
            'disable': self.run_disable
        }
        handler = command_map.get(self.args.subcommand)
        return handler() if handler else False
    
    def run_list(self) -> bool:
        """列出所有已配置的插件源
        
        Returns:
            bool: 执行结果
        """
        
        if not self._check_config_and_cache_dir():
            return False
        
        config = self._read_repo_config()
        if not config:
            return False
            
        table = PrettyTable()
        table.field_names = ["name", "url", "enabled", "available"]
        table.align["name"] = "l"  # 左对齐
        table.align["url"] = "l"   # 左对齐
        
        for section in config.sections():
            name = section
            url = config.get(section, 'url') if config.has_option(section, 'url') else ''
            enabled = config.get(section, 'enabled') if config.has_option(section, 'enabled') else 'false'
            
            # 检查缓存文件是否存在
            cache_file = os.path.join(REPO_CACHE_DIR, f"{section}.yaml")
            available = 'true' if os.path.exists(cache_file) else 'false'
            
            table.add_row([name, url, enabled, available])
            
        self.log.info("\n" + str(table))
        return True
    
    def run_update(self) -> bool:
        """更新插件索引缓存
        
        1. 读取repo.conf配置文件
        2. 对每个启用的repo下载index.yaml到缓存目录
        3. 清理不需要的缓存文件
        
        Returns:
            bool: 只要成功更新一个repo索引就返回True，否则返回False
        """
        if not self._check_config_and_cache_dir():
            return False
            
        config = self._read_repo_config()
        if not config:
            return False
            
        downloaded_files = self._process_repositories(config)
        self._cleanup_old_cache_files(downloaded_files)
        
        return len(downloaded_files) > 0
    
    def run_set(self) -> bool:
        """新增/修改插件源地址
        
        Returns:
            bool: 执行结果
        """
        name = self.args.name
        url = self.args.url
        
        config = self._read_repo_config()
        if not config:
            return False
            
        try:
            if not config.has_section(name):
                config.add_section(name)
                config.set(name, 'enabled', 'true')
                
            config.set(name, 'url', url)
            
            with open(REPO_CONFIG_PATH, 'w') as configfile:
                config.write(configfile)
                
            self.log.info(f"{'added' if not config.has_section(name) else 'updated'} repo: {name}")
            return self._download_repo_index(config, name)
        except Exception as e:
            self.log.error(f"failed to set repo {name}: {str(e)}")
            return False
    
    def run_del(self) -> bool:
        """删除指定插件源
        
        Returns:
            bool: 执行结果
        """
        name = self.args.name
        
        config = self._read_repo_config()
        if not config:
            return False
            
        if not config.has_section(name):
            self.log.error(f"Repo {name} not found")
            return False
            
        try:
            config.remove_section(name)
            with open(REPO_CONFIG_PATH, 'w') as configfile:
                config.write(configfile)
                
            self.log.info(f"removed repo: {name}")
            return self._remove_repo_cache(name)
        except Exception as e:
            self.log.error(f"failed to remove repo {name}: {str(e)}")
            return False
    
    def run_enable(self) -> bool:
        """启用插件源
        
        Returns:
            bool: 执行结果
        """
        name = self.args.name
        
        config = self._read_repo_config()
        if not config:
            return False
            
        if not config.has_section(name):
            self.log.error(f"Repo {name} not found")
            return False
            
        try:
            config.set(name, 'enabled', 'true')
            with open(REPO_CONFIG_PATH, 'w') as configfile:
                config.write(configfile)
                
            self.log.info(f"enabled repo: {name}")
            return self._download_repo_index(config, name)
        except Exception as e:
            self.log.error(f"failed to enable repo {name}: {str(e)}")
            return False
    
    def run_disable(self) -> bool:
        """禁用插件源
        
        Returns:
            bool: 执行结果
        """
        name = self.args.name
        
        config = self._read_repo_config()
        if not config:
            return False
            
        if not config.has_section(name):
            self.log.error(f"Repo {name} not found")
            return False
            
        try:
            config.set(name, 'enabled', 'false')
            with open(REPO_CONFIG_PATH, 'w') as configfile:
                config.write(configfile)
                
            self.log.info(f"disabled repo: {name}")
            return self._remove_repo_cache(name)
        except Exception as e:
            self.log.error(f"failed to disable repo {name}: {str(e)}")
            return False
    
    def _check_config_and_cache_dir(self) -> bool:
        """检查配置文件和缓存目录是否存在
        
        Returns:
            bool: 检查是否通过
        """
        if not os.path.exists(REPO_CONFIG_PATH):
            self.log.error(f"repo config file not found: {REPO_CONFIG_PATH}")
            return False
            
        if not os.path.exists(REPO_CACHE_DIR):
            self.log.error(f"cache directory not found: {REPO_CACHE_DIR}")
            return False
            
        if not os.path.exists(PLUGIN_DETAILS_DIR):
            self.log.error(f"details directory not found: {PLUGIN_DETAILS_DIR}")
            return False
        
        # 清空details目录
        for item in os.listdir(PLUGIN_DETAILS_DIR):
            item_path = os.path.join(PLUGIN_DETAILS_DIR, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                self.log.error(f"failed to delete {item_path}: {str(e)}")
                return False
        return True
    
    def _read_repo_config(self) -> configparser.ConfigParser:
        """读取repo配置文件
        
        Returns:
            ConfigParser: 解析后的配置对象，失败返回None
        """
        config = configparser.ConfigParser()
        try:
            config.read(REPO_CONFIG_PATH)
            return config
        except Exception as e:
            self.log.error(f"failed to read repo config: {str(e)}")
            return None
    
    def _process_repositories(self, config: configparser.ConfigParser) -> Set[str]:
        """处理所有启用的仓库，下载索引文件
        
        Args:
            config: 解析后的配置对象
            
        Returns:
            Set[str]: 成功下载的文件路径集合
        """
        downloaded_files = set()
        
        for section in config.sections():
            # 检查仓库是否启用
            if not (config.has_option(section, 'enabled') and 
                   config.has_option(section, 'url') and
                   config.getboolean(section, 'enabled')):
                continue
                
            index_url = config.get(section, 'url').rstrip('/') + '/index.yaml'
            output_file = os.path.join(REPO_CACHE_DIR, f"{section}.yaml")
            
            success = self._download_with_retry(index_url, output_file, section)
            if not success:
                continue
            downloaded_files.add(output_file)

            details_url = config.get(section, 'url').rstrip('/') + '/index-details.tar.gz'
            details_tmp_file = os.path.join(tempfile.gettempdir(), f"{section}-details.tar.gz")
            details_tmp_dir = os.path.join(tempfile.gettempdir(), f"{section}-details")
            
            # 下载details文件
            if not self._download_with_retry(details_url, details_tmp_file, f"{section}-details"):
                continue
                
            # 解压到临时目录
            try:
                os.makedirs(details_tmp_dir, exist_ok=True)
                try:
                    with tarfile.open(details_tmp_file, 'r:gz') as tar:
                        tar.extractall(path=details_tmp_dir)
                except Exception as e:
                    self.log.error(f"failed to extract {details_tmp_file}: {str(e)}")
                    continue
                
                # 考虑root用户与非root用户交替执行的情况，需要将权限设置为777(目录)和666(文件)
                self._set_permissions_for_details(details_tmp_dir)
                
                # 拷贝压缩文件下的子目录到details，每个子目录代表一个插件
                index_details_dir = os.path.join(details_tmp_dir, "index-details")
                if not os.path.exists(index_details_dir):
                    continue
                self._copy_details(index_details_dir)
                            
            except Exception as e:
                self.log.error(f"failed to process details for {section}: {str(e)}")
            finally:
                # 清理临时文件
                try:
                    if os.path.exists(details_tmp_file):
                        os.remove(details_tmp_file)
                    if os.path.exists(details_tmp_dir):
                        shutil.rmtree(details_tmp_dir)
                except Exception as e:
                    self.log.warning(f"failed to clean up temp files: {str(e)}")

        return downloaded_files

    def _set_permissions_for_details(self, details_dir: str):
        try:
            os.chmod(details_dir, 0o777)
            for root, dirs, files in os.walk(details_dir):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o777)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o666)
        except Exception as e:
            self.log.warning(f"failed to set permissions for {details_dir}: {str(e)}")
    
    def _copy_details(self, index_details_dir):
        for item in os.listdir(index_details_dir):
            src_path = os.path.join(index_details_dir, item)
            if not os.path.isdir(src_path):
                continue
            dst_path = os.path.join(PLUGIN_DETAILS_DIR, item)
            try:
                if os.path.exists(dst_path) and os.path.isdir(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            except Exception as e:
                self.log.error(f"failed to copy {item} to details dir: {str(e)}")
    
    def _cleanup_old_cache_files(self, downloaded_files: Set[str]):
        """清理旧的缓存文件
        
        Args:
            downloaded_files: 当前下载的文件路径集合
        """
        try:
            for filename in os.listdir(REPO_CACHE_DIR):
                if not filename.endswith('.yaml'):
                    continue
                    
                filepath = os.path.join(REPO_CACHE_DIR, filename)
                if filepath not in downloaded_files:
                    try:
                        os.remove(filepath)
                    except Exception as e:
                        self.log.error(f"failed to remove old cache file {filename}: {str(e)}")
        except Exception as e:
            self.log.error(f"failed to clean up cache directory: {str(e)}")

    def _download_repo_index(self, config: configparser.ConfigParser, name: str) -> bool:
        """下载指定repo的index.yaml文件
        
        Args:
            config: 配置对象
            name: repo名称
            
        Returns:
            bool: 下载是否成功
        """
        if not self._check_config_and_cache_dir():
            return False
            
        url = config.get(name, 'url').rstrip('/') + '/index.yaml'
        output_file = os.path.join(REPO_CACHE_DIR, f"{name}.yaml")
        
        return self._download_with_retry(url, output_file, name)

    def _remove_repo_cache(self, name: str) -> bool:
        """删除指定repo的缓存文件
        
        Args:
            name: repo名称
            
        Returns:
            bool: 删除是否成功
        """
        cache_file = os.path.join(REPO_CACHE_DIR, f"{name}.yaml")
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                self.log.info(f"removed cache file for repo: {name}")
                return True
            except Exception as e:
                self.log.error(f"failed to remove cache file {cache_file}: {str(e)}")
                return False
        return True

    def _download_with_retry(self, url: str, output_file: str, repo_name: str, max_retries: int = 3) -> bool:
        """带重试机制的下载方法
        
        Args:
            url: 下载URL
            output_file: 输出文件路径
            repo_name: 仓库名称
            max_retries: 最大重试次数
            
        Returns:
            bool: 下载是否成功
        """
        # 下载前先删除，否则可能出现因权限不足导致非root用户下载失败
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
                self.log.debug(f"removed existing file before download: {output_file}")
            except Exception as e:
                self.log.warning(f"failed to remove existing file {output_file}: {str(e)}")
        
        cmd = [
            'curl', '-fL',
            '--max-time', '10',
            '--connect-timeout', '3',
            '-o', output_file,
            url
        ]
        
        for attempt in range(max_retries):
            _, stderr, return_code = CommandExecutor.run_single_cmd(cmd)
            
            if return_code == 0:
                try:
                    self.log.info(f"download success for: {repo_name}")
                    return True
                except Exception as e:
                    self.log.error(f"failed to download {output_file}: {str(e)}")
                    return False
            
            if attempt < max_retries - 1:
                self.log.warning(f"retrying download for {repo_name} (attempt {attempt + 1}/{max_retries})")
                
        self.log.error(f"failed to download index for {repo_name} after {max_retries} attempts:\n{stderr}")
        return False
