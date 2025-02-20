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

from prettytable import PrettyTable

from src.exceptions.config_exception import ConfigException
from src.utils.log.logger_generator import LoggerGenerator
from src.utils.main_reader import MainReader


class ListCmd:
    def __init__(self, source: str):
        """
        列举源中可用的插件列表。

        :param source: 源路径
        """
        self.source = source
        self.log = LoggerGenerator().get_logger('list_cmd')

    def run(self):
        """
        列举源中可用的插件列表。

        :return: 是否执行成功
        """
        self.log.info(f'Running cmd list: source={self.source}')
        if not os.path.isdir(self.source):
            self.log.error(f'{self.source} is not a directory')
            return False
        plugin_list = []
        for item in os.listdir(self.source):
            path = os.path.join(self.source, item)
            if not item.endswith('.tar.gz'):
                continue
            try:
                main = MainReader(path)
                name = main.get_name()
                version = main.get_version()
                description = main.get_description()
            except ConfigException:
                continue
            plugin_list.append([len(plugin_list) + 1, name, version, description])
        headers = ['#', 'Plugin', 'Version', 'Description']
        table = PrettyTable(headers)
        table.add_rows(plugin_list)
        self.log.info(table.get_string())
        return True
