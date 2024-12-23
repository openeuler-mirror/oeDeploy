# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
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
