#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2025-05-28
# ======================================================================================================================

import os
import sys
import argparse
import tarfile
import yaml
import hashlib
import logging
import shutil
from datetime import datetime
from packaging import version

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_and_extract_plugin_info(tar_path):
    """验证tar.gz文件是否是合法的oeDeploy插件并提取插件信息"""
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
                logger.warning(f"Invalid plugin: missing required files in {tar_path}")
                return False, None
                
            # 提取main.yaml内容
            main_path = os.path.join(base_name, 'main.yaml')
            tar_file = tar.extractfile(main_path)
            if tar_file is None:
                logger.warning(f"Failed to extract {main_path} from {tar_path}")
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
        logger.error(f"Error processing plugin {tar_path}: {e}")
        return False, None

def calculate_sha256(file_path):
    """计算文件的sha256值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def build_plugin_entry(tar_path, plugins_dir, url_prefix, plugin_info):
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
    sha256sum = calculate_sha256(tar_path)
    
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

def load_extra_items(extra_path, plugins_dict):
    """加载并合并额外YAML文件中的插件数据
    
    Args:
        extra_path: 额外YAML文件路径
        plugins_dict: 插件字典
        
    Returns:
        bool: 是否成功加载
    """
    if not extra_path or not os.path.exists(extra_path):
        logger.error(f"Extra item file not found: {extra_path}")
        return False
    
    try:
        with open(extra_path, 'r', encoding='utf-8') as f:
            extra_data = yaml.safe_load(f)
            if not extra_data or 'plugins' not in extra_data:
                return True
            merge_extra_items(extra_data, plugins_dict)
        return True
    except Exception as e:
        logger.error(f"Error processing extra item file {extra_path}: {e}")
        return False

def merge_extra_items(extra_data, plugins_dict):
    for plugin_entry in extra_data['plugins']:
        plugin_name, versions = next(iter(plugin_entry.items()))
        if plugin_name not in plugins_dict:
            plugins_dict[plugin_name] = []
        # 过滤已存在的版本
        existing_versions = {v['version'] for v in plugins_dict[plugin_name]}
        new_versions = [v for v in versions if v['version'] not in existing_versions]
        plugins_dict[plugin_name].extend(new_versions)

def extract_plugin_to_details(tar_path, plugin_info, details_dir):
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
        logger.error(f"Error extracting plugin {tar_path} to details dir: {e}")

def compress_and_clean_details(output_dir):
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
        logger.info(f"Plugin details in {archive_path}")
            
        # 删除原目录
        shutil.rmtree(details_dir)
        
    except Exception as e:
        logger.error(f"Error compressing details dir: {e}")

def generate_index(plugins_dir, url_prefix, output_dir, extra_item=''):
    """生成index.yaml文件
    
    Args:
        plugins_dir: 插件目录路径
        url_prefix: URL前缀
        output_dir: 输出目录路径
        extra_item: 额外补充项的yaml文件路径
        
    Returns:
        bool: 是否成功生成索引文件
    """
    # 使用字典临时存储插件信息
    plugins_dict = {}
    
    # 首先处理额外补充项
    if extra_item:
        load_extra_items(os.path.abspath(extra_item), plugins_dict)
    
    if not os.path.exists(plugins_dir):
        logger.error(f"Plugins directory does not exist: {plugins_dir}")
        return False
        
    if not os.path.exists(output_dir):
        logger.error(f"Output directory does not exist: {output_dir}")
        return False
    
    # 准备index-details目录
    details_dir = os.path.join(output_dir, 'index-details')
    if os.path.exists(details_dir):
        shutil.rmtree(details_dir)
    os.makedirs(details_dir, exist_ok=True)
    
    # 遍历目录查找所有tar.gz文件
    for root, _, files in os.walk(plugins_dir):
        for file in files:
            if not file.endswith('.tar.gz'):
                continue
            
            tar_path = os.path.join(root, file)
            logger.info(f"Processing plugin: {tar_path}")
            
            # 一次性完成验证和信息提取
            valid, plugin_info = validate_and_extract_plugin_info(tar_path)
            if not valid or plugin_info is None:
                continue
                
            plugin_entry = build_plugin_entry(tar_path, plugins_dir, url_prefix, plugin_info)
            
            # 使用插件名作为key
            plugin_name = plugin_info['name']
            
            # 添加到字典
            if plugin_name not in plugins_dict:
                plugins_dict[plugin_name] = []
            plugins_dict[plugin_name].append(plugin_entry)

            # 解压插件到index-details目录
            extract_plugin_to_details(tar_path, plugin_info, details_dir)
    
    # 准备最终输出数据
    index_data = {
        'apiversion': 'v1',
        'plugins': []
    }
    
    # 按插件名排序并处理版本排序
    for plugin_name in sorted(plugins_dict.keys()):
        # 最终去重：确保name+version唯一
        seen_versions = set()
        unique_versions = []
        for v in sorted(plugins_dict[plugin_name],
                      key=lambda x: version.parse(x['version']),
                      reverse=True):
            version_key = (plugin_name, v['version'])
            if version_key not in seen_versions:
                seen_versions.add(version_key)
                unique_versions.append(v)
        
        # 添加到最终输出
        if unique_versions:
            index_data['plugins'].append({
                plugin_name: unique_versions
            })
    
    # 写入输出文件
    output_path = os.path.join(output_dir, 'index.yaml')
    fd = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        yaml.dump(index_data, f, allow_unicode=True, sort_keys=False)
    
    # 压缩并清理index-details目录
    compress_and_clean_details(output_dir)
    
    logger.info(f"Index file generated at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate oeDeploy plugin repository index file')
    parser.add_argument('plugins_dir', help='Directory containing plugin tar.gz files')
    parser.add_argument('url_prefix', help='URL prefix for plugin downloads')
    parser.add_argument('output_dir', help='Directory to output index.yaml')
    parser.add_argument('extra_item', default='', help='Path to extra items yaml file (optional)')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.plugins_dir):
        logger.error(f"Plugins directory not found: {args.plugins_dir}")
        sys.exit(1)
        
    if not os.path.isdir(args.output_dir):
        logger.error(f"Output directory not found: {args.output_dir}")
        sys.exit(1)
    
    generate_index(args.plugins_dir, args.url_prefix, args.output_dir, args.extra_item)

if __name__ == '__main__':
    main()