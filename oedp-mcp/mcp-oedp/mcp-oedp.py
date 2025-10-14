#!/usr/bin/env python3
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
# Create: 2025-03-30
# ======================================================================================================================

import argparse
import json
import os
import subprocess
import yaml
import signal
import sys
from typing import Optional, Dict, Any
from openai import OpenAI
from mcp.server.fastmcp import FastMCP


class OEDPMCPService:
    """oeDeploy MCP服务类，封装所有MCP相关功能"""

    def __init__(self, model_url: str = "", model_api_key: str = "", model_name: str = "",
                 host: str = "0.0.0.0", port: int = 8080):
        """初始化服务

        Args:
            model_url: 模型API地址
            model_api_key: 模型API密钥
            model_name: 模型名称
            host: HTTP服务器主机地址
            port: HTTP服务器端口
        """
        self.model_url = model_url
        self.model_api_key = model_api_key
        self.model_name = model_name
        self.host = host
        self.port = port
        self.mcp = None
        self._initialize_mcp()

    def _initialize_mcp(self) -> None:
        """初始化FastMCP服务器"""
        self.mcp = FastMCP(
            "安装部署命令行工具oedp调用方法",
            log_level="ERROR",
            host=self.host,
            port=self.port
        )
        self._register_tools()

    def _register_tools(self) -> None:
        """注册所有MCP工具"""
        # 注册所有工具函数
        self.mcp.tool()(self.install_oedp)
        self.mcp.tool()(self.remove_oedp)
        self.mcp.tool()(self.oedp_init_plugin)
        self.mcp.tool()(self.oedp_info_plugin)
        self.mcp.tool()(self.oedp_setup_plugin)
        self.mcp.tool()(self.oedp_run_action_plugin)
        self.mcp.tool()(self.oedp_run_install_plugin)
        self.mcp.tool()(self.oedp_run_uninstall_plugin)
        self.mcp.tool()(self.oedp_install_software_one_click)

    def update_model_config(self, model_url: str, model_api_key: str, model_name: str) -> None:
        """更新模型配置"""
        self.model_url = model_url
        self.model_api_key = model_api_key
        self.model_name = model_name

    def update_server_config(self, host: str, port: int) -> None:
        """更新服务器配置并重新初始化"""
        if host != self.host or port != self.port:
            self.host = host
            self.port = port
            self._initialize_mcp()
            print(f"服务器配置已更新: host={host}, port={port}")

    def _call_llm(self, content: str) -> Optional[str]:
        """调用LLM服务"""
        try:
            if not all([self.model_url, self.model_api_key, self.model_name]):
                return None

            client = OpenAI(api_key=self.model_api_key, base_url=self.model_url)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_CONTENT},
                    {"role": "user", "content": content}
                ]
            )
            return response.choices[0].message.content
        except Exception:
            return None

    def run(self, transport: str = 'stdio') -> None:
        """运行MCP服务器"""
        try:
            self.mcp.run(transport=transport)
        except Exception as e:
            print(f"Error starting {transport} server: {e}")
            raise

    # MCP工具方法定义
    async def install_oedp(self) -> str:
        """下载并安装noarch架构的oedp软件包(oeDeploy的命令行工具)"""
        try:
            # 下载最新版本信息文件
            latest_info_path = os.path.abspath("/tmp/latest_oedp")
            download_result = await self._download_file(LATEST_OEDP_PATH, latest_info_path)
            if download_result != "[Success]":
                return download_result

            # 读取下载URL
            with open(latest_info_path, 'r') as f:
                url = f.read().strip()

            # 从URL中提取包名
            package_name = os.path.basename(url)
            temp_file = os.path.abspath(f"/tmp/{package_name}")

            # 下载RPM包
            download_result = await self._download_file(url, temp_file)
            if download_result != "[Success]":
                return download_result

            # 安装RPM包
            result = subprocess.run(
                ["sudo", "yum", "install", "-y", temp_file],
                capture_output=True,
                text=True
            )

            # 清理临时文件
            os.remove(latest_info_path)
            os.remove(temp_file)

            if result.returncode == 0:
                return "[Success] then excute cmd: oedp repo update"
            else:
                return f"[Fail]Installation failed: {result.stderr}"

        except subprocess.CalledProcessError as e:
            return f"[Fail]Yum command failed: {str(e)}"
        except Exception as e:
            return f"[Fail]Unexpected error: {str(e)}"

    async def remove_oedp(self) -> str:
        """卸载oedp软件包(oeDeploy的命令行工具)"""
        try:
            # 执行yum remove命令
            result = subprocess.run(
                ["sudo", "yum", "remove", "-y", "oedp"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return "[Success]"
            else:
                return f"[Fail]Removal failed: {result.stderr}"

        except subprocess.CalledProcessError as e:
            return f"[Fail]Yum command failed: {str(e)}"
        except Exception as e:
            return f"[Fail]Unexpected error: {str(e)}"

    async def _download_file(self, url: str, save_path: str, timeout: int = None, max_retries: int = None) -> str:
        """下载文件并支持断点续传

        Args:
            url: 下载URL
            save_path: 文件保存路径
            timeout: 超时时间(秒)，默认使用全局配置
            max_retries: 最大重试次数，默认使用全局配置

        Returns:
            str: 成功返回"[Success]"，失败返回错误信息
        """
        timeout = timeout or DOWNLOAD_TIMEOUT
        max_retries = max_retries or DOWNLOAD_RETRIES
        temp_path = save_path + ".download"

        # 构建curl命令
        curl_cmd = [
            "curl",
            "-fL",  # 失败时不显示HTML错误页面，跟随重定向
            "-C", "-",  # 自动断点续传
            "--max-time", str(timeout),  # 设置超时时间
            "--retry", str(max_retries),  # 设置重试次数
            "--retry-delay", "2",  # 设置重试间隔(秒)
            "--output", temp_path,  # 输出到临时文件
            url
        ]

        for attempt in range(max_retries):
            try:
                # 执行curl命令
                result = subprocess.run(
                    curl_cmd,
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    # 下载完成后重命名临时文件
                    os.rename(temp_path, save_path)
                    return "[Success]"
                else:
                    if attempt == max_retries - 1:
                        return f"[Fail]Download failed after {max_retries} attempts: {result.stderr}"

            except subprocess.CalledProcessError as e:
                if attempt == max_retries - 1:
                    return f"[Fail]Download failed after {max_retries} attempts: {str(e)}"
            except Exception as e:
                if attempt == max_retries - 1:
                    return f"[Fail]Download failed after {max_retries} attempts: {str(e)}"

        return f"[Fail]Download failed after {max_retries} attempts"

    def _validate_project_structure(self, project: str) -> str:
        """校验项目目录结构

        Args:
            project: 项目目录路径
        Returns:
            str: 空字符串表示校验通过,否则返回错误信息
        """
        required_files = ["config.yaml", "main.yaml", "workspace"]
        abs_project = os.path.abspath(os.path.expanduser(project))
        for f in required_files:
            path = os.path.join(abs_project, f)
            if not os.path.exists(path):
                return f"Missing required file/directory: {f}"
        return ""

    def _check_oedp_installed(self) -> str:
        """检查oedp是否安装

        Returns:
            str: 空字符串表示已安装,否则返回错误信息
        """
        version_check = subprocess.run(
            ["oedp", "-v"],
            capture_output=True,
            text=True
        )
        if version_check.returncode != 0:
            return "oedp is not installed or not in PATH"
        return ""

    async def oedp_init_plugin(self, plugin: str, parent_dir: str) -> str:
        """获取的oeDeploy插件(又称oedp插件),并初始化

        Args:
            plugin: oeDeploy插件名称或.tar.gz文件路径/名称
            parent_dir: 插件初始化的路径,如果路径不存在,则创建
        """
        try:
            # 检查oedp是否安装
            oedp_check_result = self._check_oedp_installed()
            if oedp_check_result:
                return f"[Fail]{oedp_check_result}"

            # 确保父目录存在
            abs_parent_dir = os.path.abspath(os.path.expanduser(parent_dir))
            os.makedirs(abs_parent_dir, exist_ok=True)

            # 执行初始化命令
            result = subprocess.run(
                ["oedp", "init", plugin, "-d", abs_parent_dir, "-f"],
                capture_output=True,
                text=True
            )

            log_text = result.stdout + "\n" + result.stderr

            if result.returncode == 0:
                return "[Success]" + "\n" + log_text
            else:
                return f"[Fail]Initialization failed" + "\n" + log_text

        except subprocess.CalledProcessError as e:
            return f"[Fail]Command execution failed: {str(e)}"
        except Exception as e:
            return f"[Fail]Unexpected error: {str(e)}"

    async def oedp_info_plugin(self, project: str) -> str:
        """查询oeDeploy插件(又称oedp插件)信息,仅在明确指定project路径时触发

        Args:
            project: oeDeploy插件的项目目录, 其中必定有config.yaml,main.yaml,workspace/
        """
        # 校验项目目录结构
        abs_project = os.path.abspath(os.path.expanduser(project))
        validation_result = self._validate_project_structure(abs_project)
        if validation_result:
            return f"[Fail]{validation_result}"

        # 检查oedp是否安装
        oedp_check_result = self._check_oedp_installed()
        if oedp_check_result:
            return f"[Fail]{oedp_check_result}"

        # 执行安装命令
        try:
            result = subprocess.run(
                ["oedp", "info", "-p", abs_project],
                capture_output=True,
                text=True
            )

            log_text = result.stdout + "\n" + result.stderr

            if result.returncode == 0:
                return "[Success]" + "\n" + log_text
            else:
                return f"[Fail]Installation failed" + "\n" + log_text

        except subprocess.CalledProcessError as e:
            return f"[Fail]Command execution failed: {str(e)}"
        except Exception as e:
            return f"[Fail]Unexpected error: {str(e)}"

    async def oedp_setup_plugin(self, description: str, project: str) -> str:
        """配置oeDeploy插件(又称oedp插件): description,修改oeDeploy插件的配置文件{project}/config.yaml

        Args:
            description: 用户对oeDeploy插件config.yaml的修改说明(人类描述语言)
            project: oeDeploy插件的项目目录,其中必定有config.yaml,main.yaml,workspace/
        """
        # 校验项目目录结构
        abs_project = os.path.abspath(os.path.expanduser(project))
        validation_result = self._validate_project_structure(abs_project)
        if validation_result:
            return f"[Fail]{validation_result}"

        prompt = """
        yaml_content字段中的内容来自一个待修改的yaml文件,请根据description字段中的内容,对yaml_content进行修改.
        要求: 返回的内容中只包含修改后的yaml文本字符串,禁止包含其他任何东西,保留原来yaml文本中的注释信息.
        """

        try:
            # 读取config.yaml文件内容
            config_path = os.path.join(abs_project, "config.yaml")
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_content = f.read()

            # 构建LLM输入
            input_json = {
                "yaml_content": yaml_content,
                "description": description,
                "prompt": prompt.strip()
            }
            input_str = json.dumps(input_json, ensure_ascii=False)

            # 调用LLM获取修改后的YAML
            output = self._call_llm(input_str)
            if not output:
                return "[Fail]Failed to get response from LLM, make sure LLM api available"

            # 验证YAML格式
            try:
                yaml.safe_load(output)
            except yaml.YAMLError:
                return "[Fail]Invalid YAML format returned by LLM"

            # 备份原配置文件
            backup_path = config_path + ".bak"
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(config_path, backup_path)

            # 写入修改后的内容
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(output)

            return "[Success]Config updated successfully"

        except Exception as e:
            return f"[Fail]Unexpected error: {str(e)}"

    async def oedp_run_action_plugin(self, action: str, project: str) -> str:
        """运行oeDeploy插件(又称oedp插件)的特定操作action,仅在明确指定project路径时触发

        Args:
            action: oeDeploy插件的一个操作名称
            project: oeDeploy插件的项目目录, 其中必定有config.yaml,main.yaml,workspace/
        """
        try:
            # 校验项目目录结构
            abs_project = os.path.abspath(os.path.expanduser(project))
            validation_result = self._validate_project_structure(abs_project)
            if validation_result:
                return f"[Fail]{validation_result}"

            # 检查oedp是否安装
            oedp_check_result = self._check_oedp_installed()
            if oedp_check_result:
                return f"[Fail]{oedp_check_result}"

            # 执行命令
            result = subprocess.run(
                ["oedp", "run", action, "-p", abs_project],
                capture_output=True,
                text=True
            )

            log_text = result.stdout + "\n" + result.stderr

            if result.returncode == 0:
                return "[Success]" + "\n" + log_text
            else:
                return f"[Fail]Action execution failed" + "\n" + log_text

        except subprocess.CalledProcessError as e:
            return f"[Fail]Command execution failed: {str(e)}"
        except Exception as e:
            return f"[Fail]Unexpected error: {str(e)}"

    async def oedp_run_install_plugin(self, project: str) -> str:
        """运行oeDeploy插件(又称oedp插件)的安装部署流程,仅在明确指定project路径时触发

        Args:
            project: oeDeploy插件的项目目录, 其中必定有config.yaml,main.yaml,workspace/
        """
        try:
            # 校验项目目录结构
            abs_project = os.path.abspath(os.path.expanduser(project))
            validation_result = self._validate_project_structure(abs_project)
            if validation_result:
                return f"[Fail]{validation_result}"

            # 检查oedp是否安装
            oedp_check_result = self._check_oedp_installed()
            if oedp_check_result:
                return f"[Fail]{oedp_check_result}"

            # 执行命令
            result = subprocess.run(
                ["oedp", "run", "install", "-p", abs_project],
                capture_output=True,
                text=True
            )

            log_text = result.stdout + "\n" + result.stderr

            if result.returncode == 0:
                return "[Success]" + "\n" + log_text
            else:
                return f"[Fail]Installation failed" + "\n" + log_text

        except subprocess.CalledProcessError as e:
            return f"[Fail]Command execution failed: {str(e)}"
        except Exception as e:
            return f"[Fail]Unexpected error: {str(e)}"

    async def oedp_run_uninstall_plugin(self, project: str) -> str:
        """运行oeDeploy插件(又称oedp插件)的卸载流程,仅在明确指定project路径时触发

        Args:
            project: oeDeploy插件的项目目录, 其中必定有config.yaml,main.yaml,workspace/
        """
        try:
            # 校验项目目录结构
            abs_project = os.path.abspath(os.path.expanduser(project))
            validation_result = self._validate_project_structure(abs_project)
            if validation_result:
                return f"[Fail]{validation_result}"

            # 检查oedp是否安装
            oedp_check_result = self._check_oedp_installed()
            if oedp_check_result:
                return f"[Fail]{oedp_check_result}"

            # 执行命令
            result = subprocess.run(
                ["oedp", "run", "uninstall", "-p", abs_project],
                capture_output=True,
                text=True
            )

            log_text = result.stdout + "\n" + result.stderr

            if result.returncode == 0:
                return "[Success]" + "\n" + log_text
            else:
                return f"[Fail]Uninstallation failed" + "\n" + log_text

        except subprocess.CalledProcessError as e:
            return f"[Fail]Command execution failed: {str(e)}"
        except Exception as e:
            return f"[Fail]Unexpected error: {str(e)}"

    async def oedp_install_software_one_click(self, software: str, description: str) -> str:
        """用oeDeploy一键执行特定软件的部署流程install,仅在用户指定'oeDeploy'与'一键部署'时触发

        Args:
            software: 软件名称,可以等价于插件名称
            description: 用户对部署软件参数的描述,等价于对oeDeploy插件config.yaml的修改说明(人类描述语言)
        Returns:
            str: 执行结果与信息
        """

        # 检查oedp是否安装
        oedp_check_result = self._check_oedp_installed()
        if oedp_check_result:
            return f"[Fail]{oedp_check_result}"

        parent_dir = os.path.abspath(os.path.expanduser(DEFAULT_DIR))
        project_path = os.path.join(parent_dir, software)

        # 1. 初始化插件
        init_result = await self.oedp_init_plugin(software, parent_dir)
        if not init_result.startswith("[Success]"):
            return f"[Fail]Plugin initialization failed: {init_result}"

        # 2. 配置插件
        setup_result = await self.oedp_setup_plugin(description, project_path)
        if not setup_result.startswith("[Success]"):
            return f"[Fail]Plugin setup failed: {setup_result}"

        # 3. 运行安装
        install_result = await self.oedp_run_install_plugin(project_path)
        if not install_result.startswith("[Success]"):
            return f"[Fail]Installation failed: {install_result}"

        return "[Success]Software installed successfully"


# 全局配置常量
DEFAULT_DIR = "~/.oedp/"
DOWNLOAD_TIMEOUT = 300  # 默认超时时间(秒)
DOWNLOAD_RETRIES = 12    # 默认重试次数
LATEST_OEDP_PATH = "https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/.latest_oedp"
SYSTEM_CONTENT = """你现在是一名资深的软件工程师,你熟悉多种编程语言和开发框架,对软件开发的生命周期有深入的理解.
你擅长解决技术问题,并具有优秀的逻辑思维能力.请在这个角色下为我解答以下问题.openEuler是我默认的Linux开发环境."""


def signal_handler(sig, frame):
    """处理信号，优雅关闭服务器"""
    print("Shutting down server gracefully...")
    sys.exit(0)


def main():
    """主函数"""
    # 注册信号处理器以实现优雅关闭
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='oeDeploy MCP Server')
    parser.add_argument('--model_url', required=True, help='Model url')
    parser.add_argument('--api_key', required=True, help='API key for the vendor')
    parser.add_argument('--model_name', required=True, help='Model name')
    parser.add_argument('--transport', choices=['stdio', 'http', 'streamable-http', 'sse'], default='stdio',
                       help='Transport protocol (default: stdio). Use streamable-http for HTTP support.')
    parser.add_argument('--host', default="0.0.0.0", help='HTTP host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='HTTP port (default: 8080)')
    args = parser.parse_args()

    # 确定传输协议
    if args.transport == "http":
        transport = "streamable-http"
    else:
        transport = args.transport

    # 创建服务实例
    service = OEDPMCPService(
        model_url=args.model_url,
        model_api_key=args.api_key,
        model_name=args.model_name,
        host=args.host,
        port=args.port
    )
    
    # 打印服务器信息
    print(f"Starting MCP server with {transport} transport")
    if transport in ["streamable-http", "sse"]:
        print(f"Server will be available at http://{args.host}:{args.port}/{transport.replace('streamable-http', 'mcp')}")

    # 运行服务
    service.run(transport=transport)


if __name__ == "__main__":
    main()