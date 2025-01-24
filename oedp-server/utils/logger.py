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
# Create: 2025-01-14
# ======================================================================================================================

import logging
import os
import stat
import sys
import zipfile
from secrets import randbits

from concurrent_log_handler import ConcurrentRotatingFileHandler

from constants.paths import LOG_DIR


class LogHandler(ConcurrentRotatingFileHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream = None

    def do_gzip(self, origin_filename):
        if not zipfile:
            self._console_log("#no gzip available", stack=False)
            return
        backup_filename = origin_filename + ".zip"
        _, file_name = os.path.split(origin_filename)
        with zipfile.ZipFile(backup_filename, 'w', zipfile.ZIP_DEFLATED) as f_handler:
            f_handler.write(origin_filename, arcname=file_name)
        os.remove(origin_filename)
        self._console_log("#gzipped: %s" % (backup_filename,), stack=False)
        return

    def doRollover(self):
        self._close()
        if self.backupCount <= 0:
            self.stream = self.do_open("w")
            self._close()
            return
        tmp_name = None
        while not tmp_name or os.path.exists(tmp_name):
            bit_num = 64
            tmp_name = "%s.rotate.%08d" % (self.baseFilename, randbits(bit_num))
        try:
            os.rename(self.baseFilename, tmp_name)

            if self.use_gzip:
                self.do_gzip(tmp_name)
        except (IOError, OSError):
            exc_value = sys.exc_info()[1]
            self._console_log("rename failed.  File in use? exception=%s" % (exc_value,), stack=True)
            return

        gzip_suffix = ''
        if self.use_gzip:
            gzip_suffix = '.zip'

        def do_rename(source_file, destination_file):
            self._console_log("Rename %s -> %s" % (source_file, destination_file + gzip_suffix))
            if os.path.exists(destination_file):
                os.remove(destination_file)
            if os.path.exists(destination_file + gzip_suffix):
                os.remove(destination_file + gzip_suffix)
            source_gzip = source_file + gzip_suffix
            if os.path.exists(source_gzip):
                os.rename(source_gzip, destination_file + gzip_suffix)
            elif os.path.exists(source_file):
                os.rename(source_file, destination_file)

        for i in range(self.backupCount - 1, 0, -1):
            source_file_number = "%s.%d" % (self.baseFilename, i)
            dest_file_number = "%s.%d" % (self.baseFilename, i + 1)
            if os.path.exists(source_file_number + gzip_suffix):
                do_rename(source_file_number, dest_file_number)
        dest_file_number = self.baseFilename + ".1"
        do_rename(tmp_name, dest_file_number)

        if self.use_gzip:
            log_filename = self.baseFilename + ".1.zip"
            self._do_chown_and_chmod(log_filename)

        self._console_log("Rotation completed")


class AntiCRLFLogRecord(logging.LogRecord):
    """
    记录日志时，转义CRLF, '\n' --> '\\n'， '\r' --> '\\r'
    """

    def getMessage(self):
        """
        重写getMessage方法，以转义CRLF
        """
        messages = str(self.msg)
        if self.args:
            messages = messages % self.args
        return messages.replace('\n', '\\n').replace('\r', '\\r').replace('\f', '\\f'). \
            replace('\b', '\\b').replace('\v', '\\v').replace('\u007f', '\\u007f')


def init_log(file_name):
    """
    初始化logger
    """
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.setLogRecordFactory(AntiCRLFLogRecord)
    # 日志文件路径
    log_file = os.path.realpath(os.path.join(LOG_DIR, file_name))
    # 日志文件大小上限
    max_bytes = 10 * 1024 * 1024
    # 日志文件权限
    file_mod = 0o600
    # 日志备份数
    backup_count = 2
    # 日志级别
    log_level = "WARNING"
    # 日志输出格式
    log_format = "%(asctime)s|%(process)d:%(thread)d|%(filename)s:%(lineno)d|%(funcName)s|%(levelname)s|%(message)s"
    # 日志日期格式
    date_format = '%Y-%m-%d  %H:%M:%S %a'

    logger = logging.getLogger(file_name.split(".")[0])
    logger.setLevel(log_level)
    handler = LogHandler(log_file, maxBytes=max_bytes, chmod=file_mod, backupCount=backup_count, use_gzip=True)
    handler.setFormatter(logging.Formatter(log_format, date_format))
    if not logger.handlers:
        logger.addHandler(handler)

    if not os.path.exists(log_file):
        os.mknod(log_file)
    os.chmod(log_file, stat.S_IREAD + stat.S_IWRITE)

    return logger
