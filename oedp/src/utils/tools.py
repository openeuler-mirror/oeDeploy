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

"""
工具函数集合
"""
import importlib.util
import os
import sys


def import_from_file(filepath: str, attr_name: str):
    """
    从指定的文件中导入指定的属性，可以是类，也可以是方法等。

    :param filepath: 文件路径
    :param attr_name: 属性名称
    :return: 导入的属性，如果不存在，返回None
    """
    if not os.path.exists(filepath) or not filepath.endswith('.py'):
        return None
    file_dir = os.path.dirname(filepath)
    file_name = os.path.basename(filepath)
    module_name = os.path.splitext(file_name)[0]

    sys.path.append(file_dir)
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    attr = getattr(module, attr_name, None)
    return attr
