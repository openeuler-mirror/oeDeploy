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
from openai import OpenAI
from mcp.server.fastmcp import FastMCP

# 全局配置
DEFAULT_DIR = "~/.oedp/"
DOWNLOAD_TIMEOUT = 300  # 默认超时时间(秒)
DOWNLOAD_RETRIES = 12    # 默认重试次数
LATEST_OEDP_PATH = "https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/.latest_oedp"
SYSTEM_CONTENT = """你现在是一名资深的软件工程师,你熟悉多种编程语言和开发框架,对软件开发的生命周期有深入的理解.
你擅长解决技术问题,并具有优秀的逻辑思维能力.请在这个角色下为我解答以下问题.openEuler是我默认的Linux开发环境."""

model_url = ""
model_api_key = ""
model_name = ""

# Initialize FastMCP server
mcp = FastMCP("安装部署命令行工具oedp调用方法", log_level="ERROR")

def _call_llm(content: str) -> str:
    try:
        client = OpenAI(api_key=model_api_key, base_url=model_url)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system",
                 "content": SYSTEM_CONTENT},
                {"role": "user",
                 "content": content}
            ]
        )
        return response.choices[0].message.content
    except Exception:
        return None

async def _download_file(url: str, save_path: str, timeout: int = None, max_retries: int = None) -> str:
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

def _validate_project_structure(project: str) -> str:
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

def _check_oedp_installed() -> str:
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

@mcp.tool()
async def install_oedp() -> str:
    """下载并安装noarch架构的oedp软件包(oeDeploy的命令行工具)
    """
    try:
        # 下载最新版本信息文件
        latest_info_path = os.path.abspath("/tmp/latest_oedp")
        download_result = await _download_file(LATEST_OEDP_PATH, latest_info_path)
        if download_result != "[Success]":
            return download_result
            
        # 读取下载URL
        with open(latest_info_path, 'r') as f:
            url = f.read().strip()
            
        # 从URL中提取包名
        package_name = os.path.basename(url)
        temp_file = os.path.abspath(f"/tmp/{package_name}")
        
        # 下载RPM包
        download_result = await _download_file(url, temp_file)
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

@mcp.tool()
async def remove_oedp() -> str:
    """卸载oedp软件包(oeDeploy的命令行工具)
    """
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

@mcp.tool()
async def oedp_init_plugin(plugin: str, parent_dir: str) -> str:
    """获取的oeDeploy插件(又称oedp插件),并初始化

    Args:
        plugin: oeDeploy插件名称或.tar.gz文件路径/名称
        parent_dir: 插件初始化的路径,如果路径不存在,则创建
    """
    try:
        # 检查oedp是否安装
        oedp_check_result = _check_oedp_installed()
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

@mcp.tool()
async def oedp_info_plugin(project: str) -> str:
    """查询oeDeploy插件(又称oedp插件)信息,仅在明确指定project路径时触发

    Args:
        project: oeDeploy插件的项目目录, 其中必定有config.yaml,main.yaml,workspace/
    """
    
    # 校验项目目录结构
    abs_project = os.path.abspath(os.path.expanduser(project))
    validation_result = _validate_project_structure(abs_project)
    if validation_result:
        return f"[Fail]{validation_result}"
    
    # 检查oedp是否安装
    oedp_check_result = _check_oedp_installed()
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

@mcp.tool()
async def oedp_setup_plugin(description: str, project: str) -> str:
    """配置oeDeploy插件(又称oedp插件): description,修改oeDeploy插件的配置文件{project}/config.yaml

    Args:
        description: 用户对oeDeploy插件config.yaml的修改说明(人类描述语言)
        project: oeDeploy插件的项目目录,其中必定有config.yaml,main.yaml,workspace/
    """
    
    # 校验项目目录结构
    abs_project = os.path.abspath(os.path.expanduser(project))
    validation_result = _validate_project_structure(abs_project)
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
        output = _call_llm(input_str)
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

@mcp.tool()
async def oedp_run_action_plugin(action: str, project: str) -> str:
    """运行oeDeploy插件(又称oedp插件)的特定操作action,仅在明确指定project路径时触发

    Args:
        action: oeDeploy插件的一个操作名称
        project: oeDeploy插件的项目目录, 其中必定有config.yaml,main.yaml,workspace/
    """
    try:
        # 校验项目目录结构
        abs_project = os.path.abspath(os.path.expanduser(project))
        validation_result = _validate_project_structure(abs_project)
        if validation_result:
            return f"[Fail]{validation_result}"
        
        # 检查oedp是否安装
        oedp_check_result = _check_oedp_installed()
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

@mcp.tool()
async def oedp_run_install_plugin(project: str) -> str:
    """运行oeDeploy插件(又称oedp插件)的安装部署流程,仅在明确指定project路径时触发

    Args:
        project: oeDeploy插件的项目目录, 其中必定有config.yaml,main.yaml,workspace/
    """
    try:
        # 校验项目目录结构
        abs_project = os.path.abspath(os.path.expanduser(project))
        validation_result = _validate_project_structure(abs_project)
        if validation_result:
            return f"[Fail]{validation_result}"
        
        # 检查oedp是否安装
        oedp_check_result = _check_oedp_installed()
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

@mcp.tool()
async def oedp_run_uninstall_plugin(project: str) -> str:
    """运行oeDeploy插件(又称oedp插件)的卸载流程,仅在明确指定project路径时触发

    Args:
        project: oeDeploy插件的项目目录, 其中必定有config.yaml,main.yaml,workspace/
    """
    try:
        # 校验项目目录结构
        abs_project = os.path.abspath(os.path.expanduser(project))
        validation_result = _validate_project_structure(abs_project)
        if validation_result:
            return f"[Fail]{validation_result}"
        
        # 检查oedp是否安装
        oedp_check_result = _check_oedp_installed()
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

@mcp.tool()
async def oedp_install_software_one_click(software: str, description: str) -> str:
    """用oeDeploy一键执行特定软件的部署流程install,仅在用户指定'oeDeploy'与'一键部署'时触发
    
    Args:
        software: 软件名称,可以等价于插件名称
        description: 用户对部署软件参数的描述,等价于对oeDeploy插件config.yaml的修改说明(人类描述语言)
    Returns:
        str: 执行结果与信息
    """
    
    # 检查oedp是否安装
    oedp_check_result = _check_oedp_installed()
    if oedp_check_result:
        return f"[Fail]{oedp_check_result}"
    
    parent_dir = os.path.abspath(os.path.expanduser(DEFAULT_DIR))
    project_path = os.path.join(parent_dir, software)
    
    # 1. 初始化插件
    init_result = await oedp_init_plugin(software, parent_dir)
    if not init_result.startswith("[Success]"):
        return f"[Fail]Plugin initialization failed: {init_result}"
    
    # 2. 配置插件
    setup_result = await oedp_setup_plugin(description, project_path)
    if not setup_result.startswith("[Success]"):
        return f"[Fail]Plugin setup failed: {setup_result}"
    
    # 3. 运行安装
    install_result = await oedp_run_install_plugin(project_path)
    if not install_result.startswith("[Success]"):
        return f"[Fail]Installation failed: {install_result}"
    
    return "[Success]Software installed successfully"

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='oeDeploy MCP Server')
    parser.add_argument('--model_url', required=True, help='Model url')
    parser.add_argument('--api_key', required=True, help='API key for the vendor')
    parser.add_argument('--model_name', required=True, help='Model name')
    args = parser.parse_args()
    
    # Assign to global variables
    model_url = args.model_url
    model_api_key = args.api_key
    model_name = args.model_name
    
    # Initialize and run the server
    mcp.run(transport='stdio')
