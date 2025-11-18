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
import yaml
import hashlib
from datetime import datetime
from packaging import version
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
            'disable': self.run_disable,
            'make': self.run_make,
            'make-local': self.run_make_local
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
    
    def run_make(self) -> bool:
        """生成插件源索引文件
        
        Returns:
            bool: 执行结果
        """
        # 转换为绝对路径
        plugins_dir = os.path.abspath(self.args.plugins_dir)
        url_prefix = self.args.url_prefix
        output_dir = os.path.abspath(self.args.output_dir)
        extra_item = os.path.abspath(self.args.extra_item) if self.args.extra_item else ''
        
        # 验证目录是否存在
        if not os.path.isdir(plugins_dir):
            self.log.error(f"Plugins directory not found: {plugins_dir}")
            return False
            
        if not os.path.isdir(output_dir):
            self.log.error(f"Output directory not found: {output_dir}")
            return False
        
        return self._generate_index(plugins_dir, url_prefix, output_dir, extra_item)
    
    def run_make_local(self) -> bool:
        """生成本地插件源索引文件
        
        Args:
            path: 插件目录路径，默认为当前目录
            
        Returns:
            bool: 执行结果
        """
        path = getattr(self.args, 'path', os.getcwd())
        
        # 转换为绝对路径
        path = os.path.abspath(path)
        
        # 验证目录是否存在
        if not os.path.isdir(path):
            self.log.error(f"Directory not found: {path}")
            return False
        
        # 等价于 make 模式的参数设置
        plugins_dir = path
        url_prefix = f"file://{path}"
        output_dir = path
        extra_item = ''
        
        return self._generate_index(plugins_dir, url_prefix, output_dir, extra_item)
    
    def _validate_and_extract_plugin_info(self, tar_path: str):
        """验证tar.gz文件是否是合法的oeDeploy插件并提取插件信息
        
        Args:
            tar_path: 插件tar.gz文件路径
            
        Returns:
            tuple: (是否有效, 插件信息字典)
        """
        try:
            with tarfile.open(tar_path, 'r:gz') as tar:
                names = tar.getnames()
                base_name = os.path.basename(tar_path)[:-7]  # 去掉'.tar.gz'后缀
                
                # 检查必须的文件和目录
                required = [
                    os.path.join(base_name, 'main.yaml'),
                    os.path.join(base_name, 'config.yaml'),
                    os.path.join(base_name, 'workspace')
                ]
                
                # 如果缺少必需文件，立即返回
                if not all(item in names for item in required):
                    self.log.warning(f"Invalid plugin: missing required files in {tar_path}")
                    return False, None
                    
                # 提取main.yaml内容
                main_path = os.path.join(base_name, 'main.yaml')
                tar_file = tar.extractfile(main_path)
                if tar_file is None:
                    self.log.warning(f"Failed to extract {main_path} from {tar_path}")
                    return False, None
                    
                main_content = yaml.safe_load(tar_file.read())
                
                # 获取基本信息
                info = {
                    'name': base_name,  # name字段与插件文件名保持一致
                    'version': main_content.get('version', '1.0.0'),
                    'updated': main_content.get('updated', ''),
                    'author': main_content.get('author', ''),
                    'url': main_content.get('url', ''),
                    'description': main_content.get('description', ''),
                    'description_zh': main_content.get('description_zh', ''),
                    'description_en': main_content.get('description_en', ''),
                    'readme': main_content.get('readme', ''),
                    'icon': main_content.get('icon', ''),
                    'type': main_content.get('type', 'app'),
                    'localhost_available': main_content.get('localhost_available', False)
                }
                
                return True, info
                
        except Exception as e:
            self.log.error(f"Error processing plugin {tar_path}: {e}")
            return False, None
    
    def _calculate_sha256(self, file_path: str) -> str:
        """计算文件的sha256值
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: sha256值
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _build_plugin_entry(self, tar_path: str, plugins_dir: str, url_prefix: str, plugin_info: dict) -> dict:
        """构建插件条目字典
        
        Args:
            tar_path: 插件tar.gz文件路径
            plugins_dir: 插件目录路径
            url_prefix: URL前缀
            plugin_info: 插件信息字典
            
        Returns:
            dict: 完整的插件条目字典
        """
        # 计算文件大小和sha256
        file_size = os.path.getsize(tar_path)
        sha256sum = self._calculate_sha256(tar_path)
        
        # 构建相对路径URL，处理可能的双斜杠问题
        rel_path = os.path.relpath(tar_path, plugins_dir)
        download_url = os.path.normpath(f"{url_prefix}/{rel_path}").replace('\\', '/')
        
        # 构建插件条目
        updated_time = datetime.fromtimestamp(os.path.getmtime(tar_path)).astimezone()
        formatted_time = updated_time.strftime('%Y-%m-%dT%H:%M:%S%z')
        
        return {
            'name': plugin_info['name'],
            'version': plugin_info['version'],
            'updated': plugin_info['updated'] or formatted_time,
            'author': plugin_info['author'],
            'url': plugin_info['url'],
            'description': plugin_info['description'],
            'description_zh': plugin_info['description_zh'],
            'description_en': plugin_info['description_en'],
            'readme': plugin_info['readme'],
            'icon': plugin_info['icon'],
            'localhost_available': plugin_info['localhost_available'],
            'type': plugin_info['type'],
            'sha256sum': sha256sum,
            'size': file_size,
            'urls': [download_url]
        }
    
    def _load_extra_items(self, extra_path: str, plugins_dict: dict) -> bool:
        """加载并合并额外YAML文件中的插件数据
        
        Args:
            extra_path: 额外YAML文件路径
            plugins_dict: 插件字典
            
        Returns:
            bool: 是否成功加载
        """
        if not extra_path or not os.path.exists(extra_path):
            self.log.error(f"Extra item file not found: {extra_path}")
            return False
        
        try:
            with open(extra_path, 'r', encoding='utf-8') as f:
                extra_data = yaml.safe_load(f)
                if not extra_data or 'plugins' not in extra_data:
                    return True
                self._merge_extra_items(extra_data, plugins_dict)
            return True
        except Exception as e:
            self.log.error(f"Error processing extra item file {extra_path}: {e}")
            return False
    
    def _merge_extra_items(self, extra_data: dict, plugins_dict: dict):
        """合并额外的插件数据
        
        Args:
            extra_data: 额外数据
            plugins_dict: 插件字典
        """
        for plugin_entry in extra_data['plugins']:
            plugin_name, versions = next(iter(plugin_entry.items()))
            if plugin_name not in plugins_dict:
                plugins_dict[plugin_name] = []
            # 过滤已存在的版本
            existing_versions = {v['version'] for v in plugins_dict[plugin_name]}
            new_versions = [v for v in versions if v['version'] not in existing_versions]
            plugins_dict[plugin_name].extend(new_versions)
    
    def _extract_plugin_to_details(self, tar_path: str, plugin_info: dict, details_dir: str):
        """解压插件到index-details目录并清理workspace目录
        
        Args:
            tar_path: 插件tar.gz文件路径
            plugin_info: 插件信息字典
            details_dir: index-details目录路径
        """
        try:
            # 先解压到临时目录
            temp_dir = os.path.join(details_dir, f"temp_{os.urandom(4).hex()}")
            os.makedirs(temp_dir, exist_ok=True)
            
            # 解压文件
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(path=temp_dir)
                
            # 获取解压后的顶层目录
            extracted_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])
            
            # 重命名为目标目录 {name}_{version}
            target_dir = os.path.join(details_dir, f"{plugin_info['name']}_{plugin_info['version']}")
            os.rename(extracted_dir, target_dir)
            
            # 删除临时目录
            shutil.rmtree(temp_dir)
                
            # 删除workspace目录
            workspace_path = os.path.join(target_dir, 'workspace')
            if os.path.exists(workspace_path):
                shutil.rmtree(workspace_path)
                
        except Exception as e:
            self.log.error(f"Error extracting plugin {tar_path} to details dir: {e}")
    
    def _compress_and_clean_details(self, output_dir: str):
        """压缩index-details目录为tar.gz并删除原目录
        
        Args:
            output_dir: 输出目录路径
        """
        try:
            details_dir = os.path.join(output_dir, 'index-details')
            if not os.path.exists(details_dir):
                return
                
            # 压缩目录
            archive_path = os.path.join(output_dir, 'index-details.tar.gz')
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(details_dir, arcname='index-details')
            self.log.info(f"Plugin details in {archive_path}")
                
            # 删除原目录
            shutil.rmtree(details_dir)
            
        except Exception as e:
            self.log.error(f"Error compressing details dir: {e}")
    
    def _generate_index(self, plugins_dir: str, url_prefix: str, output_dir: str, extra_item: str = '') -> bool:
        """生成index.yaml文件
        
        Args:
            plugins_dir: 插件目录路径
            url_prefix: URL前缀
            output_dir: 输出目录路径
            extra_item: 额外补充项的yaml文件路径
            
        Returns:
            bool: 是否成功生成索引文件
        """
        # 验证目录
        if not self._validate_directories(plugins_dir, output_dir):
            return False
        
        # 初始化插件字典
        plugins_dict = {}
        if extra_item:
            self._load_extra_items(extra_item, plugins_dict)
        
        # 准备details目录
        details_dir = self._prepare_details_directory(output_dir)
        
        # 扫描并处理插件
        self._scan_and_process_plugins(plugins_dir, url_prefix, plugins_dict, details_dir)
        
        # 构建并写入索引文件
        output_path = os.path.join(output_dir, 'index.yaml')
        if not self._write_index_file(plugins_dict, output_path):
            return False
        
        # 压缩并清理details目录
        self._compress_and_clean_details(output_dir)
        
        self.log.info(f"Index file generated at: {output_path}")
        return True
    
    def _validate_directories(self, plugins_dir: str, output_dir: str) -> bool:
        """验证目录是否存在
        
        Args:
            plugins_dir: 插件目录路径
            output_dir: 输出目录路径
            
        Returns:
            bool: 验证是否通过
        """
        if not os.path.exists(plugins_dir):
            self.log.error(f"Plugins directory does not exist: {plugins_dir}")
            return False
            
        if not os.path.exists(output_dir):
            self.log.error(f"Output directory does not exist: {output_dir}")
            return False
        
        return True
    
    def _prepare_details_directory(self, output_dir: str) -> str:
        """准备index-details目录
        
        Args:
            output_dir: 输出目录路径
            
        Returns:
            str: details目录路径
        """
        details_dir = os.path.join(output_dir, 'index-details')
        if os.path.exists(details_dir):
            shutil.rmtree(details_dir)
        os.makedirs(details_dir, exist_ok=True)
        return details_dir
    
    def _scan_and_process_plugins(self, plugins_dir: str, url_prefix: str, plugins_dict: dict, details_dir: str):
        """扫描并处理所有插件
        
        Args:
            plugins_dir: 插件目录路径
            url_prefix: URL前缀
            plugins_dict: 插件字典
            details_dir: details目录路径
        """
        for root, _, files in os.walk(plugins_dir):
            for file in files:
                if not file.endswith('.tar.gz'):
                    continue
                
                tar_path = os.path.join(root, file)
                self._process_single_plugin(tar_path, plugins_dir, url_prefix, plugins_dict, details_dir)
    
    def _process_single_plugin(self, tar_path: str, plugins_dir: str, url_prefix: str, 
                               plugins_dict: dict, details_dir: str):
        """处理单个插件
        
        Args:
            tar_path: 插件tar.gz文件路径
            plugins_dir: 插件目录路径
            url_prefix: URL前缀
            plugins_dict: 插件字典
            details_dir: details目录路径
        """
        self.log.info(f"Processing plugin: {tar_path}")
        
        # 验证并提取插件信息
        valid, plugin_info = self._validate_and_extract_plugin_info(tar_path)
        if not valid or plugin_info is None:
            return
        
        # 构建插件条目
        plugin_entry = self._build_plugin_entry(tar_path, plugins_dir, url_prefix, plugin_info)
        plugin_name = plugin_info['name']
        
        # 添加到字典
        if plugin_name not in plugins_dict:
            plugins_dict[plugin_name] = []
        plugins_dict[plugin_name].append(plugin_entry)
        
        # 解压插件到details目录
        self._extract_plugin_to_details(tar_path, plugin_info, details_dir)
    
    def _write_index_file(self, plugins_dict: dict, output_path: str) -> bool:
        """写入索引文件
        
        Args:
            plugins_dict: 插件字典
            output_path: 输出文件路径
            
        Returns:
            bool: 是否成功写入
        """
        try:
            # 构建索引数据
            index_data = {
                'apiversion': 'v1',
                'plugins': self._build_sorted_plugins_list(plugins_dict)
            }
            
            # 写入文件
            fd = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                yaml.dump(index_data, f, allow_unicode=True, sort_keys=False)
            
            return True
        except Exception as e:
            self.log.error(f"Failed to write index file: {e}")
            return False
    
    def _build_sorted_plugins_list(self, plugins_dict: dict) -> list:
        """构建排序后的插件列表
        
        Args:
            plugins_dict: 插件字典
            
        Returns:
            list: 排序后的插件列表
        """
        plugins_list = []
        
        for plugin_name in sorted(plugins_dict.keys()):
            unique_versions = self._deduplicate_versions(plugin_name, plugins_dict[plugin_name])
            if unique_versions:
                plugins_list.append({plugin_name: unique_versions})
        
        return plugins_list
    
    def _deduplicate_versions(self, plugin_name: str, versions: list) -> list:
        """去重并排序插件版本
        
        Args:
            plugin_name: 插件名称
            versions: 版本列表
            
        Returns:
            list: 去重并排序后的版本列表
        """
        seen_versions = set()
        unique_versions = []
        
        # 按版本号从大到小排序
        sorted_versions = sorted(versions, key=lambda x: version.parse(x['version']), reverse=True)
        
        for v in sorted_versions:
            version_key = (plugin_name, v['version'])
            if version_key not in seen_versions:
                seen_versions.add(version_key)
                unique_versions.append(v)
        
        return unique_versions
