"""
命令行接口 - doc2plugin工具的主入口

本模块实现了doc2plugin工具的命令行接口，使用Click库提供友好的用户体验。
支持多个子命令，每个子命令都有详细的帮助信息和参数验证。
"""

import os
import sys
import click
from colorama import Fore, Style, init as colorama_init

from doc2plugin.commands import InitCommand, StatusCommand, CleanCommand
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
        project_path = os.path.abspath(path)
        
        click.echo(f"{Fore.BLUE}正在初始化项目...{Style.RESET_ALL}")
        click.echo(f"项目路径: {project_path}")
        
        if force and os.path.exists(project_path) and os.listdir(project_path):
            click.echo(f"{Fore.YELLOW}警告: 使用强制模式，目录不为空{Style.RESET_ALL}")
        
        init_cmd = InitCommand()
        
        if force:
            success = init_cmd._create_project_structure(project_path)
            if success:
                success = init_cmd._create_config_template(project_path)
            if success:
                terminal.success("项目初始化完成！")
                init_cmd._print_next_steps(project_path)
        else:
            success = init_cmd.execute(project_path)
        
        sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}操作被用户取消{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}初始化失败: {e}{Style.RESET_ALL}")
        sys.exit(1)


@main.command()
@click.option('--path', '-p', default='.', help='项目路径，默认为当前目录')
@click.option('--verbose', '-v', is_flag=True, help='显示详细输出')
@click.option('--dry-run', is_flag=True, help='预演模式，不实际执行代码编写')
def compose(path, verbose, dry_run):
    """
    执行代码编写流程
    
    启动AI Agent，根据work.yaml配置执行完整的代码编写流程。
    
    前置条件：
    - 项目已初始化（运行过doc2plugin init）
    - work.yaml配置正确的LLM信息和任务描述
    
    示例：
        doc2plugin compose                     # 在当前目录执行
        doc2plugin compose --path /tmp/demo    # 在指定目录执行
        doc2plugin compose --verbose           # 显示详细日志
        doc2plugin compose --dry-run           # 预演模式
    """
    click.echo(f"{Fore.RED}compose命令尚未实现{Style.RESET_ALL}")
    sys.exit(1)


@main.command()
@click.option('--path', '-p', default='.', help='项目路径，默认为当前目录')
@click.option('--verbose', '-v', is_flag=True, help='显示详细输出')
def test(path, verbose):
    """
    测试已生成的代码
    
    启动AI Agent，根据work.yaml配置生成测试脚本并执行。
    
    前置条件：
    - 项目已初始化（运行过doc2plugin init）
    - plugin/目录包含已生成的代码（运行过doc2plugin compose）
    
    示例：
        doc2plugin test                     # 在当前目录执行
        doc2plugin test --path /tmp/demo    # 在指定目录执行
    """
    click.echo(f"{Fore.RED}test命令尚未实现{Style.RESET_ALL}")
    sys.exit(1)


@main.command()
@click.option('--path', '-p', default='.', help='项目路径，默认为当前目录')
@click.option('--verbose', '-v', is_flag=True, help='显示详细输出')
def modify(path, verbose):
    """
    修改已生成的代码
    
    启动AI Agent，根据测试结果修改代码或测试脚本。
    
    前置条件：
    - 项目已初始化（运行过doc2plugin init）
    - 已生成测试脚本和日志（运行过doc2plugin test）
    
    示例：
        doc2plugin modify                     # 在当前目录执行
        doc2plugin modify --path /tmp/demo    # 在指定目录执行
    """
    click.echo(f"{Fore.RED}modify命令尚未实现{Style.RESET_ALL}")
    sys.exit(1)


@main.command()
@click.option('--path', '-p', default='.', help='项目路径，默认为当前目录')
@click.option('--detailed', '-d', is_flag=True, help='显示详细状态信息')
def status(path, detailed):
    """
    显示项目状态信息
    
    检查并显示项目的当前状态，包括项目结构、配置信息、文档文件等。
    
    示例：
        doc2plugin status                  # 显示基本状态
        doc2plugin status --detailed       # 显示详细状态
        doc2plugin status --path /tmp/demo # 检查指定项目
    """
    try:
        project_path = os.path.abspath(path)
        
        click.echo(f"{Fore.BLUE}检查项目状态...{Style.RESET_ALL}")
        
        status_cmd = StatusCommand()
        success = status_cmd.execute(project_path)
        
        sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}操作被用户取消{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}状态检查失败: {e}{Style.RESET_ALL}")
        sys.exit(1)


@main.command()
@click.option('--path', '-p', default='.', help='项目路径，默认为当前目录')
@click.option('--force', '-f', is_flag=True, help='强制清理，跳过确认提示')
def clean(path, force):
    """
    清理项目生成的文件
    
    删除plugin/目录内容和cache/目录中的临时文件。
    
    示例：
        doc2plugin clean                   # 清理当前项目（需要确认）
        doc2plugin clean --force           # 强制清理，跳过确认
        doc2plugin clean --path /tmp/demo  # 清理指定项目
    """
    try:
        project_path = os.path.abspath(path)
        
        if not force:
            if not click.confirm('确定要清理项目吗？这将删除所有生成的文件'):
                click.echo(f"{Fore.YELLOW}操作已取消{Style.RESET_ALL}")
                sys.exit(0)
        
        click.echo(f"{Fore.BLUE}正在清理项目...{Style.RESET_ALL}")
        
        clean_cmd = CleanCommand()
        success = clean_cmd.execute(project_path, force=force)
        
        sys.exit(0 if success else 1)
        
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


sys.excepthook = handle_exception


if __name__ == '__main__':
    main()
