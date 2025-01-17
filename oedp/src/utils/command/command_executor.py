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

import os
import signal
import subprocess
import sys


class CommandExecutor:
    """
    系统命令封装，收编挪到公共组件目录
    """

    @staticmethod
    def run_single_cmd(cmd, timeout=600, raise_exception=False, show_error=True, encoding=None, print_on_console=False):
        if encoding is None:
            encoding = sys.getdefaultencoding()

        try:
            pipe = subprocess.Popen(
                cmd, universal_newlines=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, start_new_session=True,
                encoding=encoding
            )
        except (ValueError, OSError) as error_except:
            if raise_exception:
                raise error_except
            return "", "", pipe.returncode

        try:
            stdout, stderr = CommandExecutor._get_stdout_stderr(pipe, timeout, print_on_console)
        except subprocess.TimeoutExpired as timeout_err:
            # 使用os.killpg杀死进程组
            pipe.kill()
            pipe.terminate()
            os.killpg(pipe.pid, signal.SIGTERM)
            if raise_exception:
                raise timeout_err
        except Exception as err:
            if raise_exception:
                raise err
        else:
            error = ""
            if stderr and show_error:
                error = stderr.replace("\n", "").replace("\r", "")
            return stdout, error, pipe.returncode
        return "", "", pipe.returncode

    @staticmethod
    def run_mult_cmd(cmds, timeout=600, raise_exception=False, show_error=True, encoding=None, print_on_console=False,
                     file_descriptor=None):
        if encoding is None:
            encoding = sys.getdefaultencoding()

        pipes = []
        for cmd in cmds:
            last_pipe_stdout = pipes[-1].stdout if pipes else subprocess.PIPE
            stdout_target = file_descriptor if len(pipes) == len(cmds) - 1 and file_descriptor else subprocess.PIPE
            try:
                pipe = subprocess.Popen(
                    cmd, stdin=last_pipe_stdout, universal_newlines=True, stderr=subprocess.PIPE,
                    stdout=stdout_target, start_new_session=True, encoding=encoding
                )
            except (ValueError, OSError) as error_except:
                if raise_exception:
                    raise error_except
                return "", "", pipe.returncode
            else:
                if last_pipe_stdout is not subprocess.PIPE:
                    last_pipe_stdout.close()
                pipes.append(pipe)

        try:
            stdout, stderr = CommandExecutor._get_stdout_stderr(pipes[-1], timeout, print_on_console)
        except subprocess.TimeoutExpired as timeout_err:
            # 使用os.killpg杀死进程组
            pipes[-1].kill()
            pipes[-1].terminate()
            os.killpg(pipes[-1].pid, signal.SIGTERM)
            raise timeout_err
        except Exception as err:
            if raise_exception:
                raise err
        else:
            error = ""
            if pipes[-1].returncode != 0 and len(stderr) != 0 and show_error:
                error = stderr.replace("\n", "").replace("\r", "")
            return stdout, error, pipes[-1].returncode
        return "", "", pipes[-1].returncode

    @staticmethod
    def _get_stdout_stderr(pipe, timeout, print_on_console):
        if print_on_console:
            stdout, stderr = '', ''
            for stdout_line in iter(pipe.stdout.readline, ''):
                stdout += stdout_line
                print(stdout_line, end='')
            for stderr_line in iter(pipe.stderr.readline, ''):
                stderr += stderr_line
                print(stderr_line, end='')
            pipe.wait(timeout=timeout)
        else:
            stdout, stderr = pipe.communicate(timeout=timeout)
        return stdout, stderr
