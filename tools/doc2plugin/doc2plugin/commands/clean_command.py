"""
清理命令 - 清理项目生成的文件

该命令删除plugin/目录和cache/目录中的临时文件。
"""

import os
import shutil
from doc2plugin.commands.base_command import BaseCommand
from doc2plugin.utils.terminal_output import terminal
from doc2plugin.utils.agent_logger import setup_agent_logger


class CleanCommand(BaseCommand):
    """清理命令 - 清理项目生成的文件"""
    
    def __init__(self):
        """初始化clean命令"""
        super().__init__()
        self.logger = None
    
    def execute(self, project_path: str, force: bool = False) -> bool:
        """
        执行清理命令
        
        Args:
            project_path: 项目路径
            force: 是否强制清理，跳过确认
            
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        # 设置agent日志记录器
        setup_agent_logger(project_path)
        
        terminal.info(f"开始清理项目: {project_path}")
        if force:
            terminal.info("使用强制模式，跳过确认提示")
        
        cleaned_items = []
        
        # 清理plugin目录
        plugin_dir = os.path.join(project_path, 'plugin')
        if os.path.exists(plugin_dir):
            try:
                shutil.rmtree(plugin_dir)
                os.makedirs(plugin_dir)  # 重新创建空目录
                cleaned_items.append('plugin/')
                terminal.info("已清理目录: plugin/")
            except Exception as e:
                error_msg = f"清理 plugin/ 目录失败: {e}"
                terminal.error(error_msg)
        
        # 清理cache目录中的临时文件
        cache_dir = os.path.join(project_path, 'cache')
        if os.path.exists(cache_dir):
            try:
                cache_items_removed = 0
                for item in os.listdir(cache_dir):
                    item_path = os.path.join(cache_dir, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        cache_items_removed += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        cache_items_removed += 1
                if cache_items_removed > 0:
                    cleaned_items.append('cache/*')
                    terminal.info(f"已清理 cache/ 目录中的 {cache_items_removed} 个项目")
            except Exception as e:
                error_msg = f"清理 cache/ 目录失败: {e}"
                terminal.error(error_msg)
        
        if cleaned_items:
            success_msg = f"已清理: {', '.join(cleaned_items)}"
            terminal.success(success_msg)
        else:
            warning_msg = "没有需要清理的文件"
            terminal.warning(warning_msg)
        
        return True
