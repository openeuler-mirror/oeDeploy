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
# Create: 2024-12-23
# ======================================================================================================================

import os
import glob
import yaml
import hashlib
from typing import List, Dict, Optional
from datetime import datetime

from src.constants.paths import PLUGIN_DIR, REPO_CACHE_DIR
from src.utils.command.command_executor import CommandExecutor
from src.utils.log.logger_generator import LoggerGenerator

DOWNLOAD_TIMEOUT = 600
DOWNLOAD_RETRY_TIME = 3

"""
所有路径都需要变成绝对路径后再进行实际操作
错误信息self.log.error()
提示信息self.log.info()
所有日志信息都用英文，全小写
"""

class InitCmd:
    def __init__(self, plugin: str, project: str, parent_dir: str = "", force: bool = False):
        """
        在指定的目录下初始化一个项目。

        :param plugin: 插件名称，也可以是插件压缩包路径、插件下载地址
        :param project: 项目初始化路径
        :param force: 是否强制初始化
        """
        self.plugin = plugin
        self.project = project
        self.parent_dir = parent_dir
        self.force = force
        self.log = LoggerGenerator().get_logger('init_cmd')

    def run(self):
        """
        在指定的目录下初始化一个项目。

        :return: 是否执行成功
        """
        try:
            # 1. 确定目标路径
            target_path = self._determine_target_path()
            
            # 2. 验证目标路径
            if not self._validate_target_path(target_path):
                return False
                
            # 3. 处理目标路径存在的情况
            if os.path.exists(target_path):
                if not self._handle_existing_target(target_path):
                    return False
            
            # 4. 创建目标目录
            os.makedirs(target_path, exist_ok=True)
            
            # 根据插件类型处理
            if self.plugin.endswith('.tar.gz'):
                if self.plugin.startswith(('http://', 'https://')):
                    # 5. 处理下载URL
                    filename = os.path.basename(self.plugin)
                    cache_path = os.path.join(PLUGIN_DIR, filename)
                    if not self._download_with_retry(self.plugin, cache_path, "plugin"):
                        return False
                    return self._extract_archive(cache_path, target_path)
                else:
                    # 4. 处理本地压缩包
                    return self._extract_archive(self.plugin, target_path)
            else:
                # 6. 处理插件名称
                return self._handle_plugin_name(target_path)
                
        except Exception as e:
            self.log.error(f"failed to initialize project: {str(e)}")
            return False

    def _determine_target_path(self) -> str:
        """
        plugin 如果为本地的插件压缩包，则直接初始化到指定路径
        plugin 如果为插件下载地址，则先下载到缓存路径 /var/oedp/plugin，再初始化到指定路径
        plugin 如果为插件名称，从已经配置的插件源中查找，下载到缓存路径后初始化到指定路径
        """
        if self.project:
            return os.path.abspath(self.project)
        elif self.parent_dir:
            plugin_name = os.path.splitext(os.path.basename(self.plugin))[0] if self.plugin.endswith('.tar.gz') else self.plugin
            return os.path.abspath(os.path.join(self.parent_dir, plugin_name))
        else:
            plugin_name = os.path.splitext(os.path.basename(self.plugin))[0] if self.plugin.endswith('.tar.gz') else self.plugin
            return os.path.abspath(os.path.join(os.getcwd(), plugin_name))

    def _validate_target_path(self, target_path: str) -> bool:
        """验证目标路径是否合法"""
        # 检查路径层级
        path_parts = os.path.normpath(target_path).split(os.sep)
        if len(path_parts) < 2:
            self.log.error("target path must be at least two levels deep")
            return False
        return True

    def _handle_existing_target(self, target_path: str) -> bool:
        """处理目标路径已存在的情况"""
        if os.listdir(target_path):
            if self.force:
                try:
                    for item in os.listdir(target_path):
                        item_path = os.path.join(target_path, item)
                        if os.path.isdir(item_path):
                            CommandExecutor.run_single_cmd(['rm', '-rf', item_path])
                        else:
                            os.remove(item_path)
                    self.log.info(f"cleaned existing directory: {target_path}")
                except Exception as e:
                    self.log.error(f"failed to clean directory {target_path}: {str(e)}")
                    return False
            else:
                self.log.error(f"directory {target_path} is not empty, use --force to overwrite")
                return False
        return True

    def _extract_archive(self, archive_path: str, target_path: str) -> bool:
        """解压压缩包到目标路径"""
        try:
            cmd = ['tar', '-xzf', archive_path, '-C', target_path, '--strip-components=1']
            _, stderr, return_code = CommandExecutor.run_single_cmd(cmd)
            if return_code != 0:
                self.log.error(f"failed to extract archive: {stderr}")
                return False
            self.log.info(f"successfully extracted archive to {target_path}")
            return True
        except Exception as e:
            self.log.error(f"failed to extract archive: {str(e)}")
            return False

    def _handle_plugin_name(self, target_path: str) -> bool:
        """处理插件名称"""
        try:
            # 查找插件
            plugin_info = self._find_plugin_in_repos()
            if not plugin_info:
                self.log.error(f"plugin {self.plugin} not found in any repo")
                return False
                
            # 检查本地缓存
            filename = os.path.basename(plugin_info['urls'][0])
            cache_path = os.path.join(PLUGIN_DIR, filename)
            
            if os.path.exists(cache_path) and self._verify_checksum(cache_path, plugin_info['sha256sum']):
                self.log.info(f"using cached plugin file {filename} (checksum verified)")
                return self._extract_archive(cache_path, target_path)
                
            # 尝试从URL下载
            for url in plugin_info['urls']:
                filename = os.path.basename(url)
                cache_path = os.path.join(PLUGIN_DIR, filename)
                
                if self._download_with_retry(url, cache_path, "plugin"):
                    if not self._verify_checksum(cache_path, plugin_info['sha256sum']):
                        self.log.error(f"checksum verification failed for {filename}")
                        continue
                        
                    return self._extract_archive(cache_path, target_path)
                else:
                    self.log.warning(f"failed to download from {url}")
                        
            self.log.error(f"failed to download plugin {self.plugin} from all available urls")
            return False
        except Exception as e:
            self.log.error(f"failed to handle plugin name: {str(e)}")
            return False

    def _find_plugin_in_repos(self) -> Optional[Dict]:
        """在仓库中查找插件"""
        # 遍历所有索引文件
        for index_file in glob.glob(os.path.join(REPO_CACHE_DIR, '*.yaml')):
            try:
                with open(index_file, 'r') as f:
                    data = yaml.safe_load(f)
                    
                if 'plugins' not in data:
                    continue
                    
                # 查找匹配的插件
                for plugin_entry in data['plugins']:
                    if not isinstance(plugin_entry, dict):
                        continue
                        
                    for plugin_name, versions in plugin_entry.items():
                        if plugin_name == self.plugin and versions:
                            # 找到最新版本
                            latest_version = max(
                                versions,
                                key=lambda v: (v['version'], datetime.strptime(v['updated'], "%Y-%m-%dT%H:%M:%S%z") if v.get('updated') else '')
                            )
                            return latest_version
            except Exception as e:
                self.log.warning(f"failed to parse index file {index_file}: {str(e)}")
                continue
                
        return None

    def _verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """验证文件sha256校验和"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            actual_checksum = sha256_hash.hexdigest()
            
            if actual_checksum == expected_checksum:
                return True
            else:
                return False
        except Exception as e:
            self.log.error(f"failed to verify checksum: {str(e)}")
            return False

    def _download_with_retry(self, url: str, output_file: str, repo_name: str, max_retries: int = DOWNLOAD_RETRY_TIME, timeout: int = DOWNLOAD_TIMEOUT) -> bool:
        """带重试机制的下载方法
        
        Args:
            url: 下载URL
            output_file: 输出文件路径
            repo_name: 仓库名称
            max_retries: 最大重试次数
            timeout: 下载超时时间(秒)
            
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
        
        self.log.info(f"starting download from {url}")
        cmd = [
            'curl', '-fL',
            '--max-time', str(timeout),
            '--connect-timeout', '3',
            '-o', output_file,
            url
        ]
        
        for attempt in range(max_retries):
            _, stderr, return_code = CommandExecutor.run_single_cmd(cmd)
            
            if return_code == 0:
                try:
                    self.log.info(f"successfully downloaded to {output_file}")
                    return True
                except Exception as e:
                    self.log.error(f"failed to set permissions for {output_file}: {str(e)}")
                    return False
            
            if attempt < max_retries - 1:
                self.log.warning(f"retrying download for repo {repo_name} (attempt {attempt + 1}/{max_retries})")
                
        self.log.error(f"failed to download index for repo {repo_name} after {max_retries} attempts:\n{stderr}")
        return False