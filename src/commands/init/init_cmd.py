# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
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
        self.log.info(
            f'Running cmd init: plugin={self.plugin}, source={self.source}, project={self.project}, force={self.force}')
        if not os.path.exists(self.source):
            self.log.error(f'Source path {self.source} does not exist')
            return False
        tar_name = self.plugin + '.tar.gz'
        tar_path = os.path.join(self.source, tar_name)
        if not os.path.exists(tar_path):
            self.log.info(f'Plugin {tar_name} does not exist in source {self.source}')
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
