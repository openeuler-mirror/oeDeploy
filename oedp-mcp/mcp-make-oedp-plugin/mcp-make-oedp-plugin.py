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
import os
from mcp.server.fastmcp import FastMCP

DEFAULT_DIR = "~/.oedp/"

develop_guide_path = ""

# Initialize FastMCP server
mcp = FastMCP("编写一个oeDeploy插件/oedp插件", log_level="ERROR")

@mcp.tool()
async def make_plugin_auto(plugin: str, parent_dir: str) -> str:
    """编写一个插件

    Args:
        plugin: oeDeploy插件名称,表示安装的软件或者需要执行的操作简称
        parent_dir: 插件初始化的路径,如果路径不存在,则创建;如果用户未指定,默认为~/.oedp/
    Returns:
        str: 下一步需要执行的指令
    """
    # 检查开发文档路径
    if not os.path.exists(develop_guide_path):
        return f"[Fail]开发文档不存在: {develop_guide_path}"
    
    # 检查父路径是否存在并转换为绝对路径
    if parent_dir and os.path.exists(parent_dir):
        parent_dir = os.path.abspath(os.path.expanduser(parent_dir))
    else:
        parent_dir = os.path.abspath(os.path.expanduser(DEFAULT_DIR))
    
    return "请帮我执行: {" + f"""
1. (重要!)仔细阅读oeDeploy插件的开发文档{develop_guide_path},根据用户对eDeploy插件功能的详细描述,完成对oeDeploy插件的开发.如果{parent_dir}/{plugin}目录已经存在,则清空目录中的文件
2. 开发完成后,用指定方式打包成tar.gz到{parent_dir}目录下(如果有同名文件则强制覆盖),并调用`oedp info -p {parent_dir}/{plugin}`进行测试
3. 测试通过后,不需要执行install操作
""" + "}"

if __name__ == "__main__":
    # Initialize and run the server
    parser = argparse.ArgumentParser(description='oeDeploy plugin maker MCP Server')
    parser.add_argument('--guide_path', required=True, help='develop guide doc path')
    args = parser.parse_args()
    
    # Assign to global variables
    develop_guide_path = os.path.abspath(os.path.expanduser(args.guide_path))
    if not os.path.exists(develop_guide_path):
        print(f"[Fail]开发文档不存在: {develop_guide_path}")
        exit(1)
    
    mcp.run(transport='stdio')
