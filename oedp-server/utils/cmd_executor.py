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
# Create: 2025-02-05
# ======================================================================================================================

import os
import signal
import subprocess
import sys

ERROR_CODE = 1
TIMEOUT_CODE = 2


class CommandExecutor:

    def __init__(self, cmd, encoding=sys.getdefaultencoding(), timeout=300):
        self.process = subprocess.Popen(
            cmd, universal_newlines=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, start_new_session=True,
            encoding=encoding
        )
        self.cmd = cmd
        self.timeout = timeout

    def run(self):
        try:
            stdout, stderr = self.process.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            # 终止超时进程
            self.process.kill()
            self.process.terminate()
            os.killpg(self.process.pid, signal.SIGTERM)
            return "", "", TIMEOUT_CODE
        except Exception as ex:
            # 终止异常进程
            self.process.kill()
            self.process.terminate()
            os.killpg(self.process.pid, signal.SIGTERM)
            return "", "", ERROR_CODE
        return stdout, stderr, self.process.returncode
