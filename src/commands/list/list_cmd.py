# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
# ======================================================================================================================

import os

from tabulate import tabulate

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
            print('Failed to show available plugins.')
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
            if item != f'{name}-{version}.tar.gz' and not item.startswith(f'{name}-{version}-'):
                continue
            plugin_list.append([len(plugin_list) + 1, name, version, description])
        headers = ['#', 'Plugin', 'Version', 'Description']
        print(tabulate(plugin_list, headers=headers, tablefmt='grid'))
        return True
