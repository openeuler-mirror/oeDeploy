# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
# ======================================================================================================================
import logging
import logging.handlers
import os.path

from src.constants.const import DIR_MODE, LOG_MODE_WRITING
from src.utils.log.log_config_obj import LOG_CONFIG_OBJ


class LoggerGenerator:
    def __init__(self):
        pass

    @staticmethod
    def _has_console_handler(logger):
        return any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    @staticmethod
    def _has_file_handler(logger):
        return any(isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers)


    def get_logger(self, stage: str):
        """
        返回日志对象，直接基于日志对象获取info、warn等log方法
        :param stage:oedp 后面跟的子命令名
        :return:logger对象
        """
        logger = logging.getLogger(stage)
        logger.setLevel(LOG_CONFIG_OBJ.log_level)
        if not self._has_console_handler(logger):
            self._add_console_handler(logger)
        if not self._has_file_handler(logger):
            self._add_file_handler(logger)
        return logger

    def _add_console_handler(self, logger):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_CONFIG_OBJ.console_log_level)
        console_formatter = logging.Formatter(LOG_CONFIG_OBJ.console_log_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    def _add_file_handler(self, logger):
        log_dir = os.path.dirname(LOG_CONFIG_OBJ.log_file_path)
        os.makedirs(log_dir, mode=DIR_MODE, exist_ok=True)
        self._change_file_mode_for_writing()
        file_handler = logging.handlers.RotatingFileHandler(
            filename=LOG_CONFIG_OBJ.log_file_path,
            maxBytes=LOG_CONFIG_OBJ.file_max_size,
            backupCount=LOG_CONFIG_OBJ.backup_count
        )
        file_handler.setLevel(LOG_CONFIG_OBJ.file_log_level)
        file_formatter = logging.Formatter(LOG_CONFIG_OBJ.file_log_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    def _change_file_mode_for_writing(self):
        if LOG_CONFIG_OBJ.log_file_path:
            if not os.path.exists(LOG_CONFIG_OBJ.log_file_path):
                os.fdopen(
                    os.open(LOG_CONFIG_OBJ.log_file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, LOG_MODE_WRITING),
                    'w').close()
            os.chmod(LOG_CONFIG_OBJ.log_file_path, LOG_MODE_WRITING)
