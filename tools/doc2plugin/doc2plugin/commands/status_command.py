"""
状态命令 - 显示项目状态信息

该命令显示当前项目的状态，包括配置信息、文件结构等。
"""

import os
import yaml
from doc2plugin.commands.base_command import BaseCommand
from doc2plugin.utils.terminal_output import terminal
from doc2plugin.utils.agent_logger import setup_agent_logger


class StatusCommand(BaseCommand):
    """状态命令 - 显示项目状态信息"""
    
    def __init__(self):
        """初始化status命令"""
        super().__init__()
        self.logger = None
    
    def execute(self, project_path: str) -> bool:
        """
        执行状态命令
        
        Args:
            project_path: 项目路径
            
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        # 设置agent日志记录器
        setup_agent_logger(project_path)
        
        terminal.info(f"项目状态: {project_path}")
        
        # 检查项目结构
        self._check_project_structure(project_path)
        
        # 检查配置文件
        self._check_config_status(project_path)
        
        # 检查文档文件
        self._check_documents_status(project_path)
        
        # 检查输出文件
        self._check_output_status(project_path)
        
        return True
    
    def _check_project_structure(self, project_path: str):
        """检查项目结构"""
        terminal.newline()
        terminal.info("项目结构:", 'folder')
        
        if not os.path.exists(project_path):
            terminal.error(f"项目目录不存在: {project_path}")
            return
        
        required_items = {
            'doc/': ('原始文档目录', 'folder'),
            'plugin/': ('输出脚本目录', 'folder'),
            'cache/': ('缓存目录', 'folder'),
            'work.yaml': ('配置文件', 'config'),
            'cache/source.md': ('提炼文档（可选）', 'file')
        }
        
        for item, (description, icon) in required_items.items():
            item_path = os.path.join(project_path, item)
            if os.path.exists(item_path):
                terminal.success(f"{item} - {description}", icon)
            else:
                if item == 'cache/source.md':
                    terminal.info(f"{item} - {description} (未生成)", icon)
                else:
                    terminal.warning(f"{item} - {description} (缺失)", icon)
    
    def _check_config_status(self, project_path: str):
        """检查配置状态"""
        terminal.newline()
        terminal.info("配置状态:", 'config')
        
        config_path = os.path.join(project_path, 'work.yaml')
        if not os.path.exists(config_path):
            terminal.error("配置文件不存在")
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 使用新的配置信息打印方法
            terminal.print_config_info(config)
            
            # 检查LLM配置
            if 'llm_info' in config:
                llm_info = config['llm_info']
                if llm_info.get('api_key') == 'your-api-key-here':
                    terminal.warning("API密钥未设置", 'warning')
                else:
                    terminal.success("API密钥已设置", 'check')
            
            # 检查任务配置
            if 'task' in config:
                task_info = config['task']
                target = task_info.get('target', '')
                if target and target != '请描述您的部署目标，例如：根据文档编写Nginx部署脚本':
                    terminal.success("任务目标已设置", 'check')
                else:
                    terminal.warning("任务目标未设置", 'warning')
            
        except Exception as e:
            terminal.error(f"读取配置文件失败: {e}")
    
    def _check_documents_status(self, project_path: str):
        """检查文档状态"""
        terminal.newline()
        terminal.info("文档状态:", 'doc')
        
        doc_dir = os.path.join(project_path, 'doc')
        if not os.path.exists(doc_dir):
            terminal.error("doc/ 目录不存在")
            return
        
        doc_files = []
        for root, dirs, files in os.walk(doc_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), project_path)
                doc_files.append(rel_path)
        
        if doc_files:
            terminal.print_file_list(doc_files, "文档文件")
        else:
            terminal.warning("doc/ 目录为空")
    
    def _check_output_status(self, project_path: str):
        """检查输出状态"""
        terminal.newline()
        terminal.info("输出状态:", 'script')
        
        plugin_dir = os.path.join(project_path, 'plugin')
        if not os.path.exists(plugin_dir):
            terminal.warning("plugin/ 目录不存在")
            return
        
        output_files = []
        for root, dirs, files in os.walk(plugin_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), project_path)
                output_files.append(rel_path)
        
        if output_files:
            terminal.print_file_list(output_files, "输出文件")
        else:
            terminal.info("plugin/ 目录为空", 'folder')
        
        # 检查cache/source.md
        source_md = os.path.join(project_path, 'cache', 'source.md')
        if os.path.exists(source_md):
            terminal.success("cache/source.md 已生成", 'file')
        else:
            terminal.info("cache/source.md 未生成", 'file')
