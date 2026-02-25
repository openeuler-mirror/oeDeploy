"""
初始化命令 - 创建新的doc2plugin项目

该命令在指定目录创建一个新的doc2plugin项目结构，
包括必要的目录和配置文件模板。
"""

import os
import yaml
from doc2plugin.commands.base_command import BaseCommand
from doc2plugin.utils.terminal_output import terminal
from doc2plugin.utils.agent_logger import setup_agent_logger


class InitCommand(BaseCommand):
    """初始化命令 - 创建新的doc2plugin项目"""
    
    def __init__(self):
        """初始化init命令"""
        super().__init__()
        self.logger = None
    
    def execute(self, project_path: str) -> bool:
        """
        执行初始化命令
        
        Args:
            project_path: 项目路径
            
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        terminal.info(f"正在初始化项目: {project_path}")
        
        # 检查目录是否为空
        if not self._check_empty_directory(project_path):
            return False
        
        # 目录检查通过后，再设置日志记录器
        setup_agent_logger(project_path)
        
        # 创建项目结构
        if not self._create_project_structure(project_path):
            return False
        
        # 创建配置文件模板
        if not self._create_config_template(project_path):
            return False
        
        terminal.success("项目初始化完成！")
        self._print_next_steps(project_path)
        
        return True
    
    def _check_empty_directory(self, project_path: str) -> bool:
        """检查目录是否为空"""
        if not os.path.exists(project_path):
            try:
                os.makedirs(project_path)
                terminal.info(f"创建项目目录: {project_path}")
                return True
            except Exception as e:
                terminal.error(f"无法创建项目目录: {e}")
                return False
        
        # 检查目录是否为空
        if os.listdir(project_path):
            terminal.error("项目目录不为空，请使用空目录初始化项目")
            return False
        
        return True
    
    def _create_project_structure(self, project_path: str) -> bool:
        """创建项目目录结构"""
        directories = [
            'doc',      # 原始文档目录
            'plugin',   # 输出脚本目录
            'cache',    # 缓存目录
        ]
        
        try:
            for directory in directories:
                dir_path = os.path.join(project_path, directory)
                os.makedirs(dir_path, exist_ok=True)
                terminal.info(f"创建目录: {directory}/")
            
            return True
            
        except Exception as e:
            terminal.error(f"创建项目结构时发生错误: {e}")
            return False
    
    def _create_config_template(self, project_path: str) -> bool:
        """创建配置文件模板"""
        config_template = {
            'llm_info': {
                'base_url': 'https://api.deepseek.com/v1',
                'api_key': 'your-api-key-here',
                'model_name': 'deepseek-chat',
                'timeout': 600,
                'temperature': 0.1,
                'max_tokens': None,  # 默认不限制token数量，也可以设置为具体数字如4000
                'max_llm_retries': 3,  # LLM调用最大重试次数（默认3次）
                'llm_retry_delay': 1.0  # 重试延迟（秒），使用指数退避策略（默认1.0秒）
            },
            'task': {
                'target': '请描述您的部署目标，例如：根据文档编写Nginx部署脚本',
                'prompt': '请描述环境约束和技术要求，例如：部署环境为openEuler，需要sudo权限',
                'mode': 'shell'  # 可选值: 'shell' (生成.sh脚本) 或 'oedp' (生成oeDeploy插件)
            }
        }
        
        try:
            config_path = os.path.join(project_path, 'work.yaml')
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_template, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            terminal.info("创建配置文件: work.yaml")
            return True
            
        except Exception as e:
            terminal.error(f"创建配置文件时发生错误: {e}")
            return False
    
    def _print_next_steps(self, project_path: str):
        """打印后续步骤提示"""
        terminal.newline()
        terminal.info("后续步骤:", 'task')
        terminal.info("1. 将部署文档放入 doc/ 目录", 'folder')
        terminal.info("2. 编辑 work.yaml 配置文件，填写LLM信息和任务描述", 'config')
        terminal.info("3. 运行 doc2plugin compose 开始代码编写", 'process')
