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
# Create: 2025-01-16
# ======================================================================================================================
import configparser
import os


class ConfParser:

    def __init__(self, config_file, logger=None):
        self.logger = logger
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')

    def _check_config_file(self):
        if not os.path.exists(self.config_file):
            if not self.logger:
                self.logger.warning(f"The configuration file {self.config_file} not found")
            return False
        if not os.access(self.config_file, os.R_OK):
            if not self.logger:
                self.logger.warning(f'Can not read configuration file {self.config_file}: Permission denied')
            return  False
        return True

    def get(self, section, key, default=None):
        if not self._check_config_file():
            return default
        try:
            value = self.config.get(section, key, fallback=default)
        except configparser.ParsingError as ex:
            if not self.logger:
                self.logger.warning(
                    f'The content of the configuration file {self.config_file} is incorrect, error: {ex}')
            value = default
        return value
