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
from collections import OrderedDict
from typing import Union

from utils.file_handler.base_handler import BaseHandler, FileError


class ConfHandler(BaseHandler):

    def __init__(self, **kwargs):
        """
        初始化
        :param kwargs:
            file_path  文件路径
            logger  日志记录器，当该参数不为 None 时，打印日志
            should_print  是否打印提示，当 logger 参数为 None 时才会生效，True 表示打印提示信息
        :exception:
            FileError:  配置文件校验失败时抛出
            configparser.MissingSectionHeaderError:  配置文件格式异常，文件第一行不是 section 时抛出
            configparser.ParsingError:  配置文件格式异常，不符合 .conf 文件格式时抛出
        """
        super().__init__(**kwargs)
        self.config = configparser.ConfigParser(dict_type=OrderedDict)
        # 设置大小写敏感
        self.config.optionxform = str
        if not (self._check_file_path() and self._check_file_permission()):
            raise FileError('Failed to check file.')
        try:
            self.config.read(self.file_path, encoding='utf-8')
        except (configparser.MissingSectionHeaderError, configparser.ParsingError) as ex:
            if self.logger:
                self.logger.warning(ex)
            if self.should_print:
                print(ex)
            raise ex

    def get(self, section: str, option: str, default: str = None) -> str:
        """
        获取指定的 section 和 option 的值。
        如果 section 和 option 不存在，或者在配置文件中没有为指定的 section 和 option 设置
        值，则返回 default 的值。
        :exception:  不抛出异常
        """
        value = self.config.get(section, option, fallback=default)
        if not value:
            value = default
        return value

    def getint(self, section: str, option: str, default: int = 0) -> int:
        """
        获取指定的 section 和 option 的整数值,
        如果 section 和 option 不存在，则返回 default 的值。
        :exception:
            ValueError:  当 default 不为整数，或者 value 不为整数，或者 value 为空时抛出
        """
        if not isinstance(default, int):
            msg = "The parameter 'default' must be an integer."
            if self.logger:
                self.logger.warning(msg)
            if self.should_print:
                print(msg)
            raise ValueError(msg)
        try:
            value = self.config.getint(section, option, fallback=default)
        except ValueError as ex:
            msg = "The value must be an integer and can not be empty."
            if self.logger:
                self.logger.warning(msg)
            if self.should_print:
                print(msg)
            raise ex
        return value

    def getfloat(self, section: str, option: str, default: float = 0.0) -> float:
        """
        获取指定的 section 和 option 的浮点数值,
        如果 section 和 option 不存在，则返回 default 的值。
        :exception:
            ValueError:  当 default 不为浮点数，或者 value 不为数字，或者 value 为空时抛出
        """
        if not isinstance(default, float):
            msg = "The parameter 'default' must be an float."
            if self.logger:
                self.logger.warning(msg)
            if self.should_print:
                print(msg)
            raise ValueError(msg)
        try:
            value = self.config.getfloat(section, option, fallback=default)
        except ValueError as ex:
            msg = "The value must be a number and can not be empty."
            if self.logger:
                self.logger.warning(msg)
            if self.should_print:
                print(msg)
            raise ex
        return value

    def getboolean(self, section: str, option: str, default: bool = False) -> bool:
        """
        获取指定的 section 和 option 的布尔值,
        如果 section 和 option 不存在，则返回 default 的值。
        :exception:
            ValueError:  当 default 不为布尔值，或者 value 不为 ('1', '0', 'yes', 'no', 'true', 'false', 'on', 'off')
                         其中之一，或者 value 为空时抛出
        """
        if not isinstance(default, bool):
            msg = "The parameter 'default' must be an boolean."
            if self.logger:
                self.logger.warning(msg)
            if self.should_print:
                print(msg)
            raise ValueError(msg)
        try:
            value = self.config.getboolean(section, option, fallback=default)
        except ValueError as ex:
            msg = "The specified value must be one of ('1', '0', 'yes', 'no', 'true', 'false', 'on', 'off') " \
                  "and cannot be empty."
            if self.logger:
                self.logger.warning(msg)
            if self.should_print:
                print(msg)
            raise ex
        return value

    def get_all_options(self, section: str, default: Union[None, dict] = None) -> dict:
        """
        获取指定的 section 下的所有 options 及其对应的 values。
        当 section 不存在时，返回默认值。
        :exception:  不抛出异常
        """
        if default is None:
            default = {}
        try:
            items = self.config.items(section)
        except configparser.NoSectionError:
            msg = f"The section [{section}] does not exists in the configuration file {self.file_path}."
            if self.logger:
                self.logger.warning(msg)
            if self.should_print:
                print(msg)
            return default
        if items:
            return dict(items)
        return default

    def set(self, section: str, option: str, value: str):
        """
        设置指定的 section 和 option 的 value。
        :exception:
            configparser.NoSectionError:  当指定的 section 不存在时抛出
            TypeError:  当 option 和 value 的值不会字符串时抛出
        """
        try:
            self.config.set(section, option, value)
        except configparser.NoSectionError as ex:
            msg = f"The section [{section}] does not exists in the configuration file {self.file_path}."
            if self.logger:
                self.logger.warning(msg)
            if self.should_print:
                print(msg)
            raise ex
        except TypeError as ex:
            if self.logger:
                self.logger.warning(ex)
            if self.should_print:
                print(ex)
            raise ex

    def save(self):
        """
        将调用 set() 方法产生的改定保存到文件中。
        :exception:
            FileError:  当文件校验失败时抛出
        """
        if not self._check_file_permission(os.W_OK):
            raise FileError('Failed to check file.')
        with open(self.file_path, 'w', encoding="utf-8") as f:
            self.config.write(f)
