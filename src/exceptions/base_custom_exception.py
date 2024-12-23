# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
# ======================================================================================================================

class BaseCustomException(Exception):
    """
    自定义异常基类
    """

    def __init__(self, message):
        super(BaseCustomException, self).__init__(message)
        self.message = message
