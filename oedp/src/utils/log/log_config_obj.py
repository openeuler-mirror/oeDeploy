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
import logging
import os.path
from configparser import ConfigParser, NoSectionError, NoOptionError

from src.constants.paths import LOG_CONFIG_DIR, LOG_DIR


class LogConfigObject:
    def __init__(self):
        self.config = ConfigParser()
        self.console_log_level = ""
        self.console_log_format = ""
        self.file_log_level = ""
        self.file_log_format = ""
        self.log_file_path = ""
        self.file_max_size = ""
        self.log_level = ""
        self.backup_count = ""

    def get_log_config_obj(self):
        """
        解析log.conf中的配置
        :return:
        """
        self.config.read(LOG_CONFIG_DIR, "log.conf")
        self.config = ConfigParser()
        self.config.read(os.path.join(LOG_CONFIG_DIR, "log.conf"))
        self.log_level = self._get_log_level("log")
        self.console_log_level = self._get_log_level("console_handler")
        self.console_log_format = self._get_log_format("console_handler")
        self.file_log_level = self._get_log_level("file_handler")
        self.file_log_format = self._get_log_format("file_handler")
        self.log_file_path = self.config.get("file_handler", "log_file_path",
                                             fallback=os.path.join(LOG_DIR, "oedp.log"))
        self.file_max_size = self.config.getint("file_handler", "file_max_size", fallback=5 * 1024 * 1024)
        self.backup_count = self.config.getint("file_handler", "backup_count", fallback=5)
        return self

    def _get_log_level(self, section):
        log_level = self.config.get(section, "log_level", fallback="INFO")
        level_mapping = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET,
        }
        return level_mapping.get(log_level.upper(), logging.INFO)

    def _get_log_format(self, section):
        try:
            log_format = self.config.get(section, "log_format")
        except (NoSectionError, NoOptionError):
            if section == "console_handler":
                return "[ %(levelname)s ] - [%(name)s] - %(message)s"
            if section == "file_handler":
                return "%(asctime)s [ %(levelname)s ] - [%(filename)s] [line=%(lineno)s] - [%(name)s] - %(message)s"
            return "[ %(levelname)s ] - [%(name)s] - %(message)s"
        else:
            return log_format


LOG_CONFIG_OBJ = LogConfigObject().get_log_config_obj()
