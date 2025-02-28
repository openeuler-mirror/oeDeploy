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
import shutil
import tarfile

from src.utils.log.logger_generator import LoggerGenerator


class InitCmd:
    def __init__(self, plugin: str, source: str, project: str, force: bool):
        """
        在指定的目录下初始化一个项目。

        :param plugin: 插件名称
        :param source: 源路径
        :param project: 项目初始化路径
        :param force: 是否强制初始化
        """
        self.plugin = plugin
        self.source = source
        self.project = project
        self.force = force
        self.log = LoggerGenerator().get_logger('init_cmd')

    def run(self):
        """
        在指定的目录下初始化一个项目。

        :return: 是否执行成功
        """
        self.log.debug(
            f'Running cmd init: plugin={self.plugin}, source={self.source}, project={self.project}, force={self.force}')
        if not os.path.exists(self.source):
            self.log.error(f'Source path {self.source} does not exist')
            return False
        tar_name = self.plugin + '.tar.gz'
        tar_path = os.path.join(self.source, tar_name)
        if not os.path.exists(tar_path):
            self.log.debug(f'Plugin {tar_name} does not exist in source {self.source}')
            # download
            download_success = False
            if not download_success:
                self.log.error(f'Failed to download plugin {self.plugin}')
                return False
        project_dir = os.path.dirname(self.project)
        if not os.path.exists(project_dir):
            self.log.error(f'Project path {project_dir} does not exist')
            return False
        if os.path.exists(self.project):
            if not self.force:
                self.log.error(f'Project path {self.project} already exists. Use --force to overwrite')
                return False
            try:
                shutil.rmtree(self.project)
            except OSError:
                self.log.error(f'Failed to remove {self.project}')
                return False
        try:
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(self.source)
        except tarfile.TarError:
            self.log.error(f'Failed to extract plugin {self.plugin}')
            return False
        try:
            shutil.move(os.path.join(self.source, self.plugin), self.project)
        except OSError:
            self.log.error(f'Failed to move {os.path.join(self.source, self.plugin)} to {self.project}')
            return False
        return True
