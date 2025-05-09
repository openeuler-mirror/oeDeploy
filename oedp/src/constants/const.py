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

# 命令行
import stat

# oedp 版本信息
VERSION = "1.1.0-1"

OK = 0
FAILED = 1

# 文件夹权限 750
DIR_MODE = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP
# 文件权限 640
FILE_MODE = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
# 日志权限正在记录 600
LOG_MODE_WRITING = stat.S_IRUSR | stat.S_IWUSR
