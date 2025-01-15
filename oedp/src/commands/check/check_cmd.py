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

from src.utils.log.logger_generator import LoggerGenerator


class CheckCmd:
    def __init__(self, project: str, group: str):
        """
        检查项目配置。

        :param project: 项目目录路径
        :param group: 待检查的组
        """
        self.project = project
        self.group = group
        self.log = LoggerGenerator().get_logger('check_cmd')

    def run(self):
        pass
