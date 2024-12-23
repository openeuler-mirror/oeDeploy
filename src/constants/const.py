# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
# ======================================================================================================================

# 命令行
import stat

OK = 0
FAILED = 1

# 文件夹权限 750
DIR_MODE = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP
# 文件权限 640
FILE_MODE = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
# 日志权限正在记录 600
LOG_MODE_WRITING = stat.S_IRUSR | stat.S_IWUSR
