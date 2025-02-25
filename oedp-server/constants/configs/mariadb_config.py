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
import json

from constants.paths import MARIADB_CONFIG_FILE, MARIADB_JSON_FILE
from utils.cipher import OEDPCipher
from utils.file_handler.base_handler import FileError
from utils.file_handler.conf_handler import ConfHandler

__all__ = ['MariaDBConfig', 'get_settings_mariadb_config']

DEFAULT_NAME = 'oedp_db'
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 3306
DEFAULT_USER = 'oedp'
DEFAULT_PASSWORD = ''


class MariaDBConfig:
    NAME = DEFAULT_NAME
    HOST = DEFAULT_HOST
    PORT = DEFAULT_PORT
    USER = DEFAULT_USER
    PASSWORD = DEFAULT_PASSWORD


try:
    conf_handler = ConfHandler(file_path=MARIADB_CONFIG_FILE)
except (FileError, configparser.MissingSectionHeaderError, configparser.ParsingError):
    pass
else:
    MariaDBConfig.NAME = conf_handler.get('mariadb', 'name', default=DEFAULT_NAME)
    MariaDBConfig.HOST = conf_handler.get('mariadb', 'host', default=DEFAULT_HOST)
    try:
        MariaDBConfig.PORT = conf_handler.getint('mariadb', 'port', default=DEFAULT_PORT)
    except ValueError:
        pass
    MariaDBConfig.USER = conf_handler.get('mariadb', 'user', default=DEFAULT_USER)
    MariaDBConfig.PASSWORD = conf_handler.get('mariadb', 'password', default=DEFAULT_PASSWORD)


def get_settings_mariadb_config():
    with open(MARIADB_JSON_FILE, mode='r') as fr_handle:
        ciphertext_data = json.load(fr_handle)
    oedp_cipher = OEDPCipher()
    plaintext = oedp_cipher.decrypt_ciphertext_data(ciphertext_data)
    database_config = {
        'NAME': MariaDBConfig.NAME,
        'HOST': MariaDBConfig.HOST,
        'PORT': MariaDBConfig.PORT,
        'USER': MariaDBConfig.USER,
        'PASSWORD': plaintext,
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'init_command': 'SET sql_mode="STRICT_TRANS_TABLES"',
            'charset': 'utf8',
            'autocommit': True
        },
        'TEST': {
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_bin'
        }
    }
    del plaintext
    return database_config
