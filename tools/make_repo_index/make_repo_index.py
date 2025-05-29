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
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_valid_plugin(tar_path):
    """检查tar.gz文件是否是合法的oeDeploy插件"""
    try:
        with tarfile.open(tar_path, 'r:gz') as tar:
            names = tar.getnames()
            base_name = os.path.basename(tar_path)[:-7]
            
            # 检查必须的文件和目录
            required = [
                os.path.join(base_name, 'main.yaml'),
                os.path.join(base_name, 'config.yaml'),
                os.path.join(base_name, 'workspace')
            ]
            
            return all(item in names for item in required)
    except Exception as e:
        logger.error(f"Failed to check plugin validity for {tar_path}: {e}")
        return False

def get_plugin_info(tar_path):
    """从tar.gz文件中提取插件信息"""
    try:
        with tarfile.open(tar_path, 'r:gz') as tar:
            base_name = os.path.basename(tar_path)[:-7]
            main_path = os.path.join(base_name, 'main.yaml')
            
            # 读取main.yaml内容
            tar_file = tar.extractfile(main_path)
            if tar_file is None:
                raise Exception(f"Failed to extract {main_path}")
                
            main_content = yaml.safe_load(tar_file.read())
            
            # 获取基本信息
            info = {
                'name': main_content.get('name', ''),
                'version': main_content.get('version', ''),
                'updated': main_content.get('updated', ''),
                'description': main_content.get('description', ''),
                'icon': main_content.get('icon', ''),
                'type': main_content.get('type', 'app')
            }
            
            return info
    except Exception as e:
        logger.error(f"Failed to get plugin info from {tar_path}: {e}")
        return None

def calculate_sha256(file_path):
    """计算文件的sha256值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_index(plugins_dir, url_prefix, output_dir):
    """生成index.yaml文件
    
    Args:
        plugins_dir: 插件目录路径
        url_prefix: URL前缀
        output_dir: 输出目录路径
        
    Returns:
        bool: 是否成功生成索引文件
    """
    # 使用字典临时存储插件信息
    plugins_dict = {}
    
    if not os.path.exists(plugins_dir):
        logger.error(f"Plugins directory does not exist: {plugins_dir}")
        return False
        
    if not os.path.exists(output_dir):
        logger.error(f"Output directory does not exist: {output_dir}")
        return False
    
    # 遍历目录查找所有tar.gz文件
    for root, _, files in os.walk(plugins_dir):
        for file in files:
            if not file.endswith('.tar.gz'):
                continue
            
            tar_path = os.path.join(root, file)
            logger.info(f"Processing plugin: {tar_path}")
            
            if not is_valid_plugin(tar_path):
                logger.warning(f"Invalid plugin: {tar_path}")
                continue
                
            plugin_info = get_plugin_info(tar_path)
            if plugin_info is None:
                continue
                
            # 计算文件大小和sha256
            file_size = os.path.getsize(tar_path)
            sha256sum = calculate_sha256(tar_path)
            
            # 构建相对路径URL，处理可能的双斜杠问题
            rel_path = os.path.relpath(tar_path, plugins_dir)
            download_url = os.path.normpath(f"{url_prefix}/{rel_path}").replace('\\', '/')
            
            # 构建插件条目
            updated_time = datetime.fromtimestamp(os.path.getmtime(tar_path)).astimezone()
            formatted_time = updated_time.strftime('%Y-%m-%dT%H:%M:%S%z')
            
            plugin_entry = {
                'name': plugin_info['name'],
                'version': plugin_info['version'],
                'updated': plugin_info['updated'] or formatted_time,
                'description': plugin_info['description'],
                'icon': plugin_info['icon'],
                'type': plugin_info['type'],
                'sha256sum': sha256sum,
                'size': file_size,
                'urls': [download_url]
            }
            
            # 使用插件名作为key
            plugin_name = plugin_info['name']
            
            # 添加到字典
            if plugin_name not in plugins_dict:
                plugins_dict[plugin_name] = []
            plugins_dict[plugin_name].append(plugin_entry)
    
    # 准备最终输出数据
    index_data = {
        'apiversion': 'v1',
        'plugins': []
    }
    
    # 按插件名排序并处理版本排序
    for plugin_name in sorted(plugins_dict.keys()):
        # 按版本从大到小排序
        versions = sorted(plugins_dict[plugin_name],
                         key=lambda x: x['version'],
                         reverse=True)
        
        # 添加到最终输出
        index_data['plugins'].append({
            plugin_name: versions
        })
    
    # 写入输出文件
    output_path = os.path.join(output_dir, 'index.yaml')
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(index_data, f, allow_unicode=True, sort_keys=False)
    
    logger.info(f"Index file generated at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate oeDeploy plugin repository index file')
    parser.add_argument('plugins_dir', help='Directory containing plugin tar.gz files')
    parser.add_argument('url_prefix', help='URL prefix for plugin downloads')
    parser.add_argument('output_dir', help='Directory to output index.yaml')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.plugins_dir):
        logger.error(f"Plugins directory not found: {args.plugins_dir}")
        sys.exit(1)
        
    if not os.path.isdir(args.output_dir):
        logger.error(f"Output directory not found: {args.output_dir}")
        sys.exit(1)
    
    generate_index(args.plugins_dir, args.url_prefix, args.output_dir)

if __name__ == '__main__':
    main()