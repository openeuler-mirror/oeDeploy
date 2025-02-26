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
            return ''
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
            return {}
        if not isinstance(self.main['action'], dict):
            return {}
        return self.main['action']

    def get_action_detail(self, action: str):
        """
        获取指定方法详情。

        :param action: 方法名称
        :return: 方法详情
        """
        if 'action' not in self.main:
            return {}
        if not isinstance(self.main['action'], dict):
            return {}
        if action not in self.main['action']:
            return {}
        if not isinstance(self.main['action'][action], dict):
            return {}
        return self.main['action'][action]
