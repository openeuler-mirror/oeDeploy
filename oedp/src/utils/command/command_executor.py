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

import atexit
import os
import signal
import subprocess
import sys

from src.utils.log.logger_generator import LoggerGenerator


class CommandExecutor:
    _log_file = None
    _log_file_path = None
    _atexit_registered = False
    """
    系统命令封装，收编挪到公共组件目录
    """

    @staticmethod
    def run_single_cmd(cmd, **kwargs):
        timeout = kwargs.get('timeout', 600)
        raise_exception = kwargs.get('raise_exception', False)
        show_error = kwargs.get('show_error', True)
        encoding = kwargs.get('encoding', None)
        print_on_console = kwargs.get('print_on_console', False)
        env = kwargs.get('env', None)
        log_path = kwargs.get('log_path', None)
        
        if env is not None and not isinstance(env, dict):
            raise ValueError("env parameter must be a dictionary or None")
        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        try:
            pipe = subprocess.Popen(
                cmd, universal_newlines=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, start_new_session=True,
                encoding=encoding, env=process_env
            )
        except (ValueError, OSError) as error_except:
            if raise_exception:
                raise error_except
            return "", str(error_except), 1  # 返回默认错误码，避免访问未赋值的pipe变量

        try:
            stdout, stderr = CommandExecutor._get_stdout_stderr(pipe, timeout, print_on_console, log_path)
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
    def run_mult_cmd(cmds, **kwargs):
        timeout = kwargs.get('timeout', 600)
        raise_exception = kwargs.get('raise_exception', False)
        show_error = kwargs.get('show_error', True)
        encoding = kwargs.get('encoding', None)
        print_on_console = kwargs.get('print_on_console', False)
        file_descriptor = kwargs.get('file_descriptor', None)
        env = kwargs.get('env', None)
        log_path = kwargs.get('log_path', None)
        
        if encoding is None:
            encoding = sys.getdefaultencoding()
        if env is not None and not isinstance(env, dict):
            raise ValueError("env parameter must be a dictionary or None")
        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        pipes = []
        for cmd in cmds:
            last_pipe_stdout = pipes[-1].stdout if pipes else subprocess.PIPE
            stdout_target = file_descriptor if len(pipes) == len(cmds) - 1 and file_descriptor else subprocess.PIPE
            try:
                pipe = subprocess.Popen(
                    cmd, stdin=last_pipe_stdout, universal_newlines=True, stderr=subprocess.PIPE,
                    stdout=stdout_target, start_new_session=True, encoding=encoding, env=process_env
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
            stdout, stderr = CommandExecutor._get_stdout_stderr(pipes[-1], timeout, print_on_console, log_path)
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

    @classmethod
    def _process_stream(cls, stream, output, print_on_console):
        for line in iter(stream.readline, ''):
            output += line
            log_line = line.rstrip() + "\n"
            cls._log_file.write(log_line)
            cls._log_file.flush()
            if print_on_console:
                print(line, end='')
        return output

    @classmethod
    def _get_stdout_stderr(cls, pipe, timeout, print_on_console, log_path=None):
        stdout, stderr = '', ''
        
        # 初始化直接日志文件写入
        if log_path and (cls._log_file is None or cls._log_file_path != log_path):
            if cls._log_file:
                cls._log_file.close()
            cls._log_file_path = log_path
            cls._log_file = open(log_path, 'a', buffering=1)  # 行缓冲
        elif cls._log_file is None:
            cls._log_file_path = LoggerGenerator().get_logger('command_executor').handlers[1].baseFilename
            cls._log_file = open(cls._log_file_path, 'a', buffering=1)  # 行缓冲
        
        # 注册atexit处理函数
        if not cls._atexit_registered:
            atexit.register(cls.cleanup_resources)
            cls._atexit_registered = True
        
        stdout = cls._process_stream(pipe.stdout, stdout, print_on_console)
        stderr = cls._process_stream(pipe.stderr, stderr, print_on_console)

        pipe.wait(timeout=timeout)
        return stdout, stderr

    @classmethod
    def cleanup_resources(cls):
        """清理类持有的文件描述符"""
        if cls._log_file is not None:
            try:
                cls._log_file.close()
            except Exception as e:
                LoggerGenerator().get_logger('command_executor').error(f"Failed to close log file: {str(e)}")
            cls._log_file = None
