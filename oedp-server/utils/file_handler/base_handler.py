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

import os


class FileError(Exception):

    def __int__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class BaseHandler:
    
    def __init__(self, file_path=None, logger=None, should_print=False):
        self.file_path = file_path
        self.logger = logger
        if self.logger:
            should_print = False
        self.should_print = should_print
        
    def _check_file_path(self) -> bool:
        """
        检查文件路径是否存在，存在则返回 True
        """
        if not os.path.exists(self.file_path):
            msg = f"The file {self.file_path} not found"
            if self.logger:
                self.logger.warning(msg)
            if self.should_print:
                print(msg)
            return False
        return True

    def _check_file_permission(self, mode=os.R_OK) -> bool:
        """
        检查是否有操作文件的权限, 有权限则返回 True
        """
        if not os.access(self.file_path, mode):
            msg = f'Can not operate file {self.file_path}: Permission denied'
            if self.logger:
                self.logger.warning(msg)
            if self.should_print:
                print(msg)
            return False
        return True
