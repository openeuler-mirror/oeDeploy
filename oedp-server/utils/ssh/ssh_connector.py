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
# Create: 2025-02-13
# ======================================================================================================================

import pexpect

from constants.configs.ssh_conf import SSHConfig
from constants.paths import SSH_PROMPTS_JSON_FILE
from utils.cipher import OEDPCipher
from utils.file_handler.json_handler import JSONHandler
from utils.logger import init_log
from utils.ssh.base_connector import BaseConnector

run_logger = init_log("run.log")


class SSHEstablishError(Exception):

    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message


class SSHCmdError(Exception):

    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message


class SSHCmdTimeoutError(SSHCmdError):

    def __init__(self, message):
        super().__init__(message)


class SSHConnector(BaseConnector):
    # 根据匹配到的提示符判断当前 SSH 连接的状态
    IN_PROGRESS = "In Progress"
    SUCCESS = "Success"
    FAIL = "Fail"

    # ssh_prompts.json 文件中的密码占位符
    PW_PLACEHOLDER = "PASSWORD"

    # 命令执行结果和命名返回码之间的分隔符
    DELIMITER = "##oedpEMCSL##"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expect_prompts = JSONHandler(file_path=SSH_PROMPTS_JSON_FILE, logger=run_logger).data
        self._establish()

    def _check_login_status(self, idx, login_prompt_data, child):
        prompt_dict = login_prompt_data[idx]
        if prompt_dict.get("status") == self.SUCCESS:
            run_logger.info("Successfully logged in")
            return True
        if prompt_dict.get("status") == self.FAIL:
            run_logger.error("SSH connection failed, error as follows:")
            run_logger.error(f"buffer: {str(child.buffer).strip()}")
            run_logger.error(f"before_expect: {str(child.before).strip()}")
            run_logger.error(f"after_expect: {str(child.after).strip()}")
            raise SSHEstablishError("SSH connection failed")
        if prompt_dict.get("status") == self.IN_PROGRESS:
            return False

    def _establish(self):
        run_logger.info("==== Start to establish SSH connection ====")

        # 创建一个 SSH 子进程 和 child 对象，child 对象用于和子进程交互
        run_logger.info("Start to launch an SSH subprocess")
        establish_cmd = f"ssh -o PreferredAuthentications=password -p {self.port} {self.username}@{self.ip}"
        try:
            child = pexpect.spawn(establish_cmd, encoding='utf-8', timeout=SSHConfig.ESTABLISH_TIMEOUT)
        except pexpect.exceptions.ExceptionPexpect as ex:
            run_logger.info(f"Failed to establish an SSH connection, error: {str(ex)}")
            raise SSHEstablishError(str(ex)) from ex
        run_logger.info("Successfully launched SSH subprocess")

        # 登录
        run_logger.info("Start to log in")
        login_prompt_data = self.expect_prompts.get("login")
        login_prompt_data.append({
            "prompt": pexpect.TIMEOUT,
            "send": None,
            "status": "Fail",
            "message": "SSH connection failed. Error: Timeout or no matching prompt",
            "next": None
        })
        login_prompt_data.append({
            "prompt": pexpect.EOF,
            "send": None,
            "status": "Fail",
            "message": "SSH connection failed. Error: The SSH connection subprocess has exited",
            "next": None
        })
        login_prompts = [_.get("prompt") for _ in login_prompt_data if _.get("prompt")]
        idx = child.expect(login_prompts, timeout=SSHConfig.ESTABLISH_TIMEOUT)
        if self._check_login_status(idx, login_prompt_data, child):
            self.connection = child
            return
        else:
            prompt_dict = login_prompt_data[idx]
            while True:
                send_str = prompt_dict.get("send")
                prompt_dict = prompt_dict.get("next")
                if send_str == self.PW_PLACEHOLDER:
                    # 解密密文数据字典，获取明文密码字典
                    run_logger.info("Start to decrypt the password")
                    oedp_oedpcipher = OEDPCipher()
                    plaintext_dict = oedp_oedpcipher.decrypt_ciphertext_data(self.ciphertext_data)
                    run_logger.info("successfully decrypted password")
                    send_str = plaintext_dict.get("password")
                    del plaintext_dict
                child.sendline(send_str)
                if prompt_dict is None:
                    break
        idx = child.expect(login_prompts, timeout=SSHConfig.ESTABLISH_TIMEOUT)
        if self._check_login_status(idx, login_prompt_data, child):
            self.connection = child

        run_logger.info("==== Successfully established SSH connection ====")

    def _set_window_size(self, cmd):
        window_height = SSHConfig.WINDOW_HEIGHT
        window_width = len(cmd) + SSHConfig.WINDOW_BUFFER_WIDTH
        if self.connection:
            self.connection.setwinsize(window_height, window_width)

    def execute_cmd(self, cmd, timeout=SSHConfig.EXECUTE_CMD_TIMEOUT):
        run_logger.info(f"==== Start to execute command [{cmd}] ====")

        cmd_ = f'res=$({cmd}); echo "$res{self.DELIMITER}$?"'
        expect_prompt = f'\r\n.*{self.DELIMITER}[0-9]+'
        self._set_window_size(cmd_)
        self.connection.sendline(cmd_)
        try:
            self.connection.expect(expect_prompt, timeout=timeout)
        except pexpect.TIMEOUT:
            msg = f"Command [{cmd}] timed out"
            run_logger.error(msg)
            raise SSHCmdTimeoutError(msg)
        except pexpect.EOF:
            msg = "SSH subprocess exited abnormally during command execution"
            run_logger.error(msg)
            raise SSHCmdTimeoutError(msg)
        res = str(self.connection.after).split(self.DELIMITER)
        return_code = res[-1]
        std = res[-2].strip('$?"').strip()
        if not return_code.isdigit():
            msg = f"The return code ({return_code}) is not a number"
            run_logger.error(msg)
            raise ValueError(msg)
        run_logger.info(f"The return code: {return_code}. The command's output: {std}")

        run_logger.info(f"==== Successfully executed command ====")
        return std, return_code
