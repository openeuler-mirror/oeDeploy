"""
终端输出管理器 - 基于 Rich 库实现

功能特性：
- 美化的终端输出（图标和颜色）
- Spinner 动画（使用 rich.spinner）
- 流式内容显示（使用 rich.live）
- 自动日志记录（同步记录到agent.log）
- Transient 模式：动画结束后自动清除，保持终端整洁
"""

import re
from contextlib import contextmanager
from typing import Optional

from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text

from doc2plugin.utils.agent_logger import get_agent_logger


class TerminalOutput:
    """
    终端输出管理器 - 基于 Rich 库
    
    提供美化的终端输出功能，包括图标、颜色、动态加载动画等。
    """
    
    # 图标定义
    ICONS = {
        'info': '🔍',
        'success': '✅', 
        'error': '❌',
        'warning': '⚠️',
        'llm': '🤖',
        'file': '📄',
        'folder': '📁',
        'script': '🔧',
        'doc': '📝',
        'check': '✔️',
        'process': '⚙️',
        'save': '💾',
        'read': '📖',
        'write': '✏️',
        'clean': '🧹',
        'config': '⚙️',
        'task': '📋',
        'extract': '📤',
        'develop': '🛠️',
        'quality': '🔍',
        'skip': '⏭️',
        'summary': '📊'
    }
    
    def __init__(self):
        """初始化终端输出管理器"""
        self.console = Console()
        self._live = None
        self._streaming_content = ""
    
    def _log_message(self, icon: str, message: str, level: str = 'INFO'):
        """将消息记录到agent.log"""
        try:
            logger = get_agent_logger()
            # 移除ANSI颜色代码
            clean_message = self._remove_ansi_codes(f"{icon} {message}")
            if level == 'INFO':
                logger.info(clean_message)
            elif level == 'WARNING':
                logger.warning(clean_message)
            elif level == 'ERROR':
                logger.error(clean_message)
        except RuntimeError:
            # logger未初始化，忽略（比如在init命令的早期阶段）
            pass
    
    def _remove_ansi_codes(self, text: str) -> str:
        """移除ANSI颜色代码"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _print_with_icon(self, icon: str, message: str, style: str = "", log_level: str = 'INFO'):
        """打印带图标的消息，并记录到日志"""
        text = Text(f"{icon} {message}")
        if style:
            text.stylize(style)
        self.console.print(text)
        self._log_message(icon, message, log_level)
    
    def info(self, message: str, icon: str = 'info'):
        """打印信息消息"""
        icon_char = self.ICONS.get(icon, self.ICONS['info'])
        self._print_with_icon(icon_char, message, "blue", 'INFO')
    
    def success(self, message: str, icon: str = 'success'):
        """打印成功消息"""
        icon_char = self.ICONS.get(icon, self.ICONS['success'])
        self._print_with_icon(icon_char, message, "green", 'INFO')
    
    def error(self, message: str, icon: str = 'error'):
        """打印错误消息"""
        icon_char = self.ICONS.get(icon, self.ICONS['error'])
        self._print_with_icon(icon_char, message, "red", 'ERROR')
    
    def warning(self, message: str, icon: str = 'warning'):
        """打印警告消息"""
        icon_char = self.ICONS.get(icon, self.ICONS['warning'])
        self._print_with_icon(icon_char, message, "yellow", 'WARNING')
    
    def llm_start(self, message: str):
        """LLM调用开始"""
        icon_char = self.ICONS['llm']
        self._print_with_icon(icon_char, message, "cyan", 'INFO')
    
    def llm_success(self, message: str):
        """LLM调用成功"""
        icon_char = self.ICONS['check']
        self._print_with_icon(icon_char, message, "green", 'INFO')
    
    def file_operation(self, message: str, operation: str = 'file'):
        """文件操作消息"""
        icon_char = self.ICONS.get(operation, self.ICONS['file'])
        self._print_with_icon(icon_char, message, "magenta", 'INFO')
    
    def process_step(self, message: str, step_icon: str = 'process'):
        """处理步骤消息"""
        icon_char = self.ICONS.get(step_icon, self.ICONS['process'])
        self._print_with_icon(icon_char, message, "blue", 'INFO')
    
    @contextmanager
    def spinner(self, message: str):
        """
        上下文管理器：显示旋转动画，支持流式内容更新
        
        Args:
            message: 要显示的消息
            
        Usage:
            with terminal.spinner("正在处理..."):
                # 执行耗时操作
                # 可以调用 terminal.update_streaming_content() 更新显示
        """
        self._streaming_content = ""
        spinner = Spinner("dots", text=message, style="cyan")
        
        with Live(spinner, console=self.console, refresh_per_second=10, transient=True) as live:
            self._live = live
            try:
                yield
            finally:
                self._live = None
                self._streaming_content = ""
    
    def update_streaming_content(self, content: str):
        """更新流式内容"""
        if self._live:
            self._streaming_content = content
            # 截断过长的内容
            max_length = min(self.console.width // 2, 48)
            display_content = content
            if len(content) > max_length:
                display_content = "..." + content[-(max_length - 3):]
            
            # 清理空白字符
            display_content = ' '.join(display_content.split())
            
            # 更新显示
            spinner = Spinner("dots", text=display_content, style="cyan")
            self._live.update(spinner)
    
    def append_streaming_content(self, content: str):
        """追加流式内容"""
        self._streaming_content += content
        self.update_streaming_content(self._streaming_content)
    
    def print_step_header(self, step_num: int, title: str, icon: str = 'process'):
        """打印步骤标题"""
        icon_char = self.ICONS.get(icon, self.ICONS['process'])
        self.console.print()
        self.console.rule(f"[yellow]{icon_char} 步骤 {step_num}: {title}[/yellow]")
        
        try:
            logger = get_agent_logger()
            logger.info("")
            logger.info("=" * 50)
            logger.info(f"{icon_char} 步骤 {step_num}: {title}")
            logger.info("=" * 50)
        except RuntimeError:
            pass
    
    def print_file_list(self, files: list, title: str = "文件列表"):
        """打印文件列表"""
        if not files:
            self.warning(f"{title}: 无文件")
            return
            
        self.info(f"{title}: 共 {len(files)} 个文件", 'folder')
        for i, file_path in enumerate(files, 1):
            if i <= 5:
                self.info(f"  {i}. {file_path}", 'file')
            elif i == 6:
                self.info(f"  ... 还有 {len(files) - 5} 个文件", 'file')
                break
    
    def print_config_info(self, config: dict):
        """打印配置信息"""
        self.info("配置信息:", 'config')
        
        if 'llm_info' in config:
            llm = config['llm_info']
            self.info(f"  模型: {llm.get('model_name', '未设置')}")
            self.info(f"  API地址: {llm.get('base_url', '未设置')}")
            
        if 'task' in config:
            task = config['task']
            self.info(f"  模式类型: {task.get('mode', '未设置')}")
            target = task.get('target', '')
            if len(target) > 50:
                target = target[:47] + "..."
            self.info(f"  任务目标: {target}")
    
    def print_banner(self, version: str):
        """打印工具横幅"""
        banner_text = f"""
[cyan]╔══════════════════════════════════════════════════════════════╗
║                        doc2plugin v{version}                        ║
║                                                              ║
║        AI Agent工具 - 智能代码编写助手                         ║
║                     基于LangChain开发                        ║
╚══════════════════════════════════════════════════════════════╝[/cyan]
"""
        self.console.print(banner_text)
        
        try:
            logger = get_agent_logger()
            banner_plain = f"""
╔══════════════════════════════════════════════════════════════╗
║                        doc2plugin v{version}                        ║
║                                                              ║
║        AI Agent工具 - 智能代码编写助手                         ║
║                     基于LangChain开发                        ║
╚══════════════════════════════════════════════════════════════╝
"""
            logger.info(banner_plain)
        except RuntimeError:
            pass
    
    def newline(self):
        """打印空行"""
        self.console.print()
        try:
            logger = get_agent_logger()
            logger.info("")
        except RuntimeError:
            pass


# 全局终端输出实例
terminal = TerminalOutput()
