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

from src.exceptions.base_custom_exception import BaseCustomException


class ConfigException(BaseCustomException):
    """
    元数据解析异常
    """

    def __init__(self, message):
        super(BaseCustomException, self).__init__(message)
        self.message = message

    def __str__(self):
        if not str(self.message).startswith('Reading config error: '):
            return 'Reading config error: ' + str(self.message)
        return self.message
