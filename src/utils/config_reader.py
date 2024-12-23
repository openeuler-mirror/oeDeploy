# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
# ======================================================================================================================

import json
import os

import yaml

from src.exceptions.config_exception import ConfigException


def _get_key_word_map():
    key_word_map = {}
    key_word_map_file = 'key_word_map.json'
    if os.path.exists(key_word_map_file):
        with open(key_word_map_file, 'r', encoding='utf-8') as f:
            key_word_map = json.load(f)
    return key_word_map


_key_word_map = _get_key_word_map()


class ConfigReader:
    def __init__(self, project):
        """
        读取指定项目目录下的配置文件。

        :param project: 项目目录的路径
        """
        if not os.path.exists(project):
            raise ConfigException(f'Project {project} not found')

        config_file = os.path.join(project, 'config.yaml')
        if not os.path.exists(config_file):
            raise ConfigException(f'Config file {config_file} not found')

        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def config2inventory(self):
        if 'all' not in self.config:
            raise ConfigException(f'Missing "all" in config file')
        inventory = {'all': {}}
        self._read_group(self.config['all'], inventory['all'])
        return inventory

    @staticmethod
    def _read_group(source: dict, result: dict):
        if 'children' in source:
            result['children'] = {}
            for name, subgroup in source['children'].items():
                result['children'][name] = {}
                ConfigReader._read_group(subgroup, result['children'][name])
        if 'hosts' in source:
            result['hosts'] = {}
            for name, host in source['hosts'].items():
                result['hosts'][name] = {}
                ConfigReader._read_host(host, result['hosts'][name])
        if 'vars' in source:
            result['vars'] = {}
            for name, var in source['vars'].items():
                result['vars'][name] = var

    @staticmethod
    def _read_host(source: dict, result: dict):
        for key, value in source.items():
            if key in _key_word_map:
                result[_key_word_map[key]] = value
            else:
                result[key] = value
