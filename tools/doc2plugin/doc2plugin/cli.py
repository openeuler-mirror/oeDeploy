"""
命令行接口 - doc2plugin工具的主入口

本模块实现了doc2plugin工具的命令行接口，使用Click库提供友好的用户体验。
支持多个子命令，每个子命令都有详细的帮助信息和参数验证。
"""

import os
import sys
import traceback
import click
from colorama import Fore, Style, init as colorama_init

from doc2plugin.commands import InitCommand, ComposeCommand, TestCommand, ModifyCommand, StatusCommand, CleanCommand
from doc2plugin.utils.terminal_output import terminal
from doc2plugin import __version__

# 初始化colorama
colorama_init()


def print_banner():
    """打印工具横幅"""
    terminal.print_banner(__version__)


@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help='显示版本信息')
@click.pass_context
def main(ctx, version):
    """
    doc2plugin - AI Agent工具，智能代码编写助手
    
    这个工具使用LangChain框架开发，能够智能分析部署文档，
    自动生成对应的部署脚本和用户文档。
    
    使用流程：
    1. doc2plugin init          # 初始化项目
    2. 将文档放入doc/目录
    3. 编辑work.yaml配置文件
    4. doc2plugin compose       # 执行代码编写
    
    更多信息请访问项目文档。
    """
    if version:
        click.echo(f"doc2plugin version {__version__}")
        return
    
    if ctx.invoked_subcommand is None:
        print_banner()
        click.echo(ctx.get_help())


@main.command()
@click.option('--path', '-p', default='.', 
              help='项目路径，默认为当前目录')
@click.option('--force', '-f', is_flag=True,
              help='强制初始化，即使目录不为空')
def init(path, force):
    """
    初始化新的doc2plugin项目
    
    在指定目录创建项目结构，包括：
    - doc/          原始文档目录
    - plugin/       输出脚本目录  
    - cache/        缓存目录
    - work.yaml     配置文件模板
    
    示例：
        doc2plugin init                    # 在当前目录初始化
        doc2plugin init --path /tmp/demo   # 在指定目录初始化
        doc2plugin init --force            # 强制初始化非空目录
    """
    try:
        # 转换为绝对路径
        project_path = os.path.abspath(path)
        
        click.echo(f"{Fore.BLUE}正在初始化项目...{Style.RESET_ALL}")
        click.echo(f"项目路径: {project_path}")
        
        # 检查强制模式
        if force and os.path.exists(project_path) and os.listdir(project_path):
            click.echo(f"{Fore.YELLOW}警告: 使用强制模式，目录不为空{Style.RESET_ALL}")
        
        # 执行初始化命令
        init_cmd = InitCommand()
        
        # 如果是强制模式，跳过空目录检查
        if force:
            # 直接创建结构，不检查空目录
            success = init_cmd._create_project_structure(project_path)
            if success:
                success = init_cmd._create_config_template(project_path)
            if success:
                terminal.success("项目初始化完成！")
                init_cmd._print_next_steps(project_path)
        else:
            success = init_cmd.execute(project_path)
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}操作被用户取消{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}初始化失败: {e}{Style.RESET_ALL}")
        sys.exit(1)


@main.command()
@click.option('--path', '-p', default='.', 
              help='项目路径，默认为当前目录')
@click.option('--verbose', '-v', is_flag=True,
              help='显示详细输出')
@click.option('--dry-run', is_flag=True,
              help='预演模式，不实际执行代码编写')
def compose(path, verbose, dry_run):
    """
    执行代码编写流程
    
    启动AI Agent，根据work.yaml配置执行完整的代码编写流程：
    1. 分析doc/目录下的文档
    2. 提炼关键信息到cache/source.md
    3. 生成部署脚本到plugin/目录
    4. 编写用户文档
    
    前置条件：
    - 项目已初始化（运行过doc2plugin init）
    - doc/目录包含部署文档（可选）
    - work.yaml配置正确的LLM信息和任务描述
    
    示例：
        doc2plugin compose                     # 在当前目录执行
        doc2plugin compose --path /tmp/demo    # 在指定目录执行
        doc2plugin compose --verbose           # 显示详细日志
        doc2plugin compose --dry-run           # 预演模式
    """
    try:
        # 转换为绝对路径
        project_path = os.path.abspath(path)
        
        click.echo(f"{Fore.BLUE}正在执行代码编写...{Style.RESET_ALL}")
        click.echo(f"项目路径: {project_path}")
        
        if dry_run:
            click.echo(f"{Fore.YELLOW}预演模式：不会实际执行代码编写{Style.RESET_ALL}")
            # 在预演模式下，只进行验证，不实际执行代码编写
            compose_cmd = ComposeCommand()
            success = (compose_cmd._validate_project_structure(project_path) and
                      compose_cmd._check_documents(project_path) and
                      compose_cmd._validate_config(project_path))
            
            if success:
                click.echo(f"{Fore.GREEN}预演检查通过，可以执行代码编写{Style.RESET_ALL}")
            else:
                click.echo(f"{Fore.RED}预演检查失败{Style.RESET_ALL}")
        else:
            # 执行实际代码编写
            compose_cmd = ComposeCommand()
            success = compose_cmd.execute(project_path)
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}操作被用户取消{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}执行失败: {e}{Style.RESET_ALL}")
        if verbose:
            click.echo(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
        sys.exit(1)


@main.command()
@click.option('--path', '-p', default='.', 
              help='项目路径，默认为当前目录')
@click.option('--verbose', '-v', is_flag=True,
              help='显示详细输出')
def test(path, verbose):
    """
    测试已生成的代码
    
    启动AI Agent，根据work.yaml配置生成测试脚本并执行：
    1. 读取已生成的plugin/目录下的代码
    2. 读取cache/source.md（提纯后的文档）
    3. 根据测试指导文档生成测试脚本cache/test.sh
    4. 执行测试脚本并输出结果到cache/test.log
    
    前置条件：
    - 项目已初始化（运行过doc2plugin init）
    - plugin/目录包含已生成的代码（运行过doc2plugin compose）
    - work.yaml配置正确的LLM信息和任务描述
    
    示例：
        doc2plugin test                     # 在当前目录执行
        doc2plugin test --path /tmp/demo    # 在指定目录执行
        doc2plugin test --verbose           # 显示详细日志
    """
    try:
        # 转换为绝对路径
        project_path = os.path.abspath(path)
        
        click.echo(f"{Fore.BLUE}正在执行测试...{Style.RESET_ALL}")
        click.echo(f"项目路径: {project_path}")
        
        # 执行测试命令
        test_cmd = TestCommand()
        success = test_cmd.execute(project_path)
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}操作被用户取消{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}执行失败: {e}{Style.RESET_ALL}")
        if verbose:
            click.echo(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
        sys.exit(1)


@main.command()
@click.option('--path', '-p', default='.', 
              help='项目路径，默认为当前目录')
@click.option('--verbose', '-v', is_flag=True,
              help='显示详细输出')
def modify(path, verbose):
    """
    修改已生成的代码
    
    启动AI Agent，根据测试结果修改代码或测试脚本：
    1. 读取cache/source.md（提纯后的文档）
    2. 读取已生成的plugin/目录下的代码
    3. 读取cache/test.sh测试脚本
    4. 读取cache/test.log测试日志
    5. 分析失败原因，生成修改计划
    6. 执行修改任务，修改相关文件
    
    前置条件：
    - 项目已初始化（运行过doc2plugin init）
    - plugin/目录包含已生成的代码（运行过doc2plugin compose）
    - 已生成测试脚本和日志（运行过doc2plugin test）
    - work.yaml配置正确的LLM信息和任务描述
    
    示例：
        doc2plugin modify                     # 在当前目录执行
        doc2plugin modify --path /tmp/demo    # 在指定目录执行
        doc2plugin modify --verbose           # 显示详细日志
    """
    try:
        # 转换为绝对路径
        project_path = os.path.abspath(path)
        
        click.echo(f"{Fore.BLUE}正在执行代码修改...{Style.RESET_ALL}")
        click.echo(f"项目路径: {project_path}")
        
        # 执行修改命令
        modify_cmd = ModifyCommand()
        success = modify_cmd.execute(project_path)
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}操作被用户取消{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}执行失败: {e}{Style.RESET_ALL}")
        if verbose:
            click.echo(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
        sys.exit(1)


@main.command()
@click.option('--path', '-p', default='.', 
              help='项目路径，默认为当前目录')
@click.option('--detailed', '-d', is_flag=True,
              help='显示详细状态信息')
def status(path, detailed):
    """
    显示项目状态信息
    
    检查并显示项目的当前状态，包括：
    - 项目结构完整性
    - 配置文件状态
    - 文档文件情况
    - 输出文件情况
    
    这个命令可以帮助诊断项目配置问题。
    
    示例：
        doc2plugin status                  # 显示基本状态
        doc2plugin status --detailed       # 显示详细状态
        doc2plugin status --path /tmp/demo # 检查指定项目
    """
    try:
        # 转换为绝对路径
        project_path = os.path.abspath(path)
        
        click.echo(f"{Fore.BLUE}检查项目状态...{Style.RESET_ALL}")
        
        # 执行状态检查
        status_cmd = StatusCommand()
        success = status_cmd.execute(project_path)
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}操作被用户取消{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}状态检查失败: {e}{Style.RESET_ALL}")
        sys.exit(1)


@main.command()
@click.option('--path', '-p', default='.', 
              help='项目路径，默认为当前目录')
@click.option('--force', '-f', is_flag=True,
              help='强制清理，跳过确认提示')
def clean(path, force):
    """
    清理项目生成的文件
    
    删除以下文件和目录：
    - plugin/ 目录及其内容
    - cache/ 目录中的临时文件（含source.md）
    
    注意：此操作不可逆，请谨慎使用。
    
    示例：
        doc2plugin clean                   # 清理当前项目（需要确认）
        doc2plugin clean --force           # 强制清理，跳过确认
        doc2plugin clean --path /tmp/demo  # 清理指定项目
    """
    try:
        # 转换为绝对路径
        project_path = os.path.abspath(path)
        
        # 如果不是强制模式，需要确认
        if not force:
            if not click.confirm('确定要清理项目吗？这将删除所有生成的文件'):
                click.echo(f"{Fore.YELLOW}操作已取消{Style.RESET_ALL}")
                sys.exit(0)
        
        click.echo(f"{Fore.BLUE}正在清理项目...{Style.RESET_ALL}")
        
        # 执行清理命令
        clean_cmd = CleanCommand()
        success = clean_cmd.execute(project_path, force=force)
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"{Fore.RED}清理失败: {e}{Style.RESET_ALL}")
        sys.exit(1)


def handle_exception(exc_type, exc_value, exc_traceback):
    """全局异常处理器"""
    if issubclass(exc_type, KeyboardInterrupt):
        click.echo(f"\n{Fore.YELLOW}操作被用户取消{Style.RESET_ALL}")
        sys.exit(1)
    
    click.echo(f"{Fore.RED}发生未预期的错误: {exc_value}{Style.RESET_ALL}")
    sys.exit(1)


# 设置全局异常处理器
sys.excepthook = handle_exception


if __name__ == '__main__':
    main()
