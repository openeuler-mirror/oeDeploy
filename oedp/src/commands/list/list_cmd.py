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
import yaml
from prettytable import PrettyTable

from src.constants.paths import REPO_CACHE_DIR
from src.utils.log.logger_generator import LoggerGenerator


class ListCmd:
    def __init__(self):
        """
        列举插件源中可用的插件列表。
        """
        self.log = LoggerGenerator().get_logger('list_cmd')

    def run(self):
        """
        列举插件源中可用的插件列表。

        :return: 是否执行成功
        """
        if not os.path.exists(REPO_CACHE_DIR):
            self.log.error(f"repo cache directory not found: {REPO_CACHE_DIR}")
            return False
            
        try:
            table = self._create_table()
            has_data = False
            
            for filename in os.listdir(REPO_CACHE_DIR):
                if not filename.endswith('.yaml'):
                    continue
                    
                filepath = os.path.join(REPO_CACHE_DIR, filename)
                repo_name = os.path.splitext(filename)[0]
                has_data |= self._process_yaml_file(filepath, repo_name, table)
                
            if has_data:
                self.log.info("\n" + str(table))
            else:
                self.log.info("No plugins found in repository cache")
                
            return True
            
        except Exception as e:
            self.log.error(f"failed to list plugins: {str(e)}")
            return False
            
    def _create_table(self):
        """创建并配置输出表格"""
        table = PrettyTable()
        table.field_names = ["repo", "name", "version", "updated", "type", "size", "description"]
        table.align["name"] = "l"
        table.align["version"] = "l"
        table.align["updated"] = "l"
        table.align["size"] = "r"
        table.align["description"] = "l"
        table._max_width = {"description": 64}
        return table
        
    def _process_yaml_file(self, filepath, repo_name, table):
        """处理单个yaml文件并填充表格数据"""
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
                
            if not data or 'plugins' not in data:
                return False
                
            has_data = False
            for plugin in data['plugins']:
                # 每个plugin是一个字典，key是插件名，value是版本列表
                for plugin_name, versions in plugin.items():
                    for version_info in versions:
                        row = [
                            repo_name,
                            version_info.get('name', plugin_name),
                            version_info.get('version', ''),
                            version_info.get('updated', ''),
                            version_info.get('type', ''),
                            version_info.get('size', ''),
                            version_info.get('description', '')
                        ]
                        table.add_row(row)
                        has_data = True
                        
            return has_data
            
        except Exception as e:
            self.log.error(f"failed to process {filepath}: {str(e)}")
            return False
