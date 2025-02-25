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
# Create: 2025-02-14
# ======================================================================================================================

import json
import os

from utils.file_handler.base_handler import BaseHandler, FileError


class JSONHandler(BaseHandler):

    def __init__(self, **kwargs):
        """
        初始化
        :param kwargs:
            file_path  文件路径
            logger  日志记录器，当该参数不为 None 时，打印日志
            should_print  是否打印提示，当 logger 参数为 None 时才会生效，True 表示打印提示信息
        :exception:
            FileError:  当文件校验失败后抛出
            json.JSONDecodeError:  当 JSON 文件格式异常时抛出
        """
        super().__init__(**kwargs)
        self.data = None
        self._read()

    def _read(self):
        """
        读取 JSON 文件内容
        :exception:
            FileError:  当文件校验失败后抛出
            json.JSONDecodeError:  当 JSON 文件格式异常时抛出
        """
        if not (self._check_file_path() and self._check_file_permission()):
            raise FileError('Failed to check file.')
        try:
            with open(self.file_path, 'r') as file:
                self.data = json.load(file)
        except json.JSONDecodeError as ex:
            if self.logger:
                self.logger.warning(ex)
            if self.should_print:
                print(ex)
            raise ex

    def save(self):
        """
        保存修改内容
        :exception:
            FileError:  当文件校验失败后抛出
        """
        if self._check_file_permission(mode=os.W_OK):
            raise FileError('Failed to check file.')
        with os.fdopen(os.open(
            self.file_path,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            0o640
        ), 'w') as file:
            json.dump(self.data, file, indent=2)
