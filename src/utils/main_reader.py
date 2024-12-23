# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
# ======================================================================================================================

import os

import tarfile
import yaml

from src.exceptions.config_exception import ConfigException


class MainReader:
    def __init__(self, project: str):
        """
        读取指定项目目录下的元数据文件。

        :param project: 项目目录的路径
        """

        if project.endswith('.tar.gz'):
            base_name = os.path.basename(project)[:-7]
            try:
                with tarfile.open(project, 'r:gz') as tar:
                    tar_names = tar.getnames()

                    main_path = os.path.join(base_name, 'main.yaml')
                    if main_path not in tar_names:
                        raise ConfigException(f'Main info file not found in {project}')

                    tar_file = tar.extractfile(main_path)
                    if tar_file is not None:
                        self.main = yaml.safe_load(tar_file.read())
                    else:
                        raise ConfigException(f"Failed to extract {main_path} from {project}")
            except tarfile.TarError as e:
                raise ConfigException(f'Failed to extract {project}: {e}')

        else:
            if not os.path.exists(project):
                raise ConfigException(f'Project {project} not found')

            main_file = os.path.join(project, 'main.yaml')
            if not os.path.exists(main_file):
                raise ConfigException(f'Main info file {main_file} not found')

            with open(main_file, 'r', encoding='utf-8') as f:
                self.main = yaml.safe_load(f)

    def get_name(self):
        """
        获取元数据中提供的项目名称。

        :return: 当前项目的名称
        """
        if 'name' not in self.main:
            raise ConfigException(f'Key "name" not found')
        return str(self.main['name'])

    def get_version(self):
        """
        获取元数据中提供的项目版本。

        :return: 当前项目的版本
        """
        if 'version' not in self.main:
            raise ConfigException(f'Key "version" not found')
        return str(self.main['version'])

    def get_description(self):
        """
        获取元数据中提供的项目说明。

        :return: 当前项目的说明
        """
        if 'description' not in self.main:
            return ''
        if self.main['description'] is None:
            return ''
        return str(self.main['description'])

    def get_action(self):
        """
        获取元数据中提供的可用方法。

        :return: 当前项目的可用方法
        """
        if 'action' not in self.main:
            raise ConfigException(f'Key "action" not found')
        if not isinstance(self.main['action'], dict):
            raise ConfigException(f'Key "action" must be a dict')
        return self.main['action']

    def get_action_detail(self, action: str):
        """
        获取指定方法详情。

        :param action: 方法名称
        :return: 方法详情
        """
        if 'action' not in self.main:
            raise ConfigException(f'Key "action" not found')
        if not isinstance(self.main['action'], dict):
            raise ConfigException(f'Key "action" must be a dict')
        if action not in self.main['action']:
            raise ConfigException(f'Action "{action}" not found')
        return self.main['action'][action]
