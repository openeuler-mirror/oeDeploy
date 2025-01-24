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

from enum import Enum

from constants.paths import MARIADB_CONFIG_FILE, SECRET_KEY_FILE
from utils.cipher import decrypt_mariadb_passwd
from utils.config_parser import ConfParser

config_parser = ConfParser(MARIADB_CONFIG_FILE)


class MariaDBConfig(Enum):
    NAME = config_parser.get('mariadb', 'name', default='oedp_db')
    HOST = config_parser.get('mariadb', 'host', default='127.0.0.1')
    PORT = config_parser.get('mariadb', 'port', default=3306)
    USER = config_parser.get('mariadb', 'user', default='oedp')
    PASSWORD = config_parser.get('mariadb', 'password', default='')


def get_settings_mariadb_config():
    plaintext = decrypt_mariadb_passwd(SECRET_KEY_FILE, MariaDBConfig.PASSWORD)
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