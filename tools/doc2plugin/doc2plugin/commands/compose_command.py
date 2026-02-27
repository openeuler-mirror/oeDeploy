"""
代码编写命令 - 执行代码编写流程

该命令启动AI Agent，根据配置文件执行完整的代码编写流程，
基于doc/目录下的文档自动生成plugin/目录下的可执行脚本。
"""

import traceback
from doc2plugin.commands.base_command import BaseCommand
from doc2plugin.utils.terminal_output import terminal
from doc2plugin.utils.project_manager import ProjectManager
from doc2plugin.utils.agent_logger import setup_agent_logger, get_agent_logger
from doc2plugin.agent.core import Doc2PluginAgent


class ComposeCommand(BaseCommand):
    """代码编写命令 - 执行代码编写流程"""
    
    def __init__(self):
        """初始化compose命令"""
        super().__init__()
        self.logger = None
    
    def execute(self, project_path: str) -> bool:
        """
        执行代码编写命令
        
        Args:
            project_path: 项目路径
            
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        # 设置agent日志记录器
        setup_agent_logger(project_path)
        self.logger = get_agent_logger()
        
        terminal.info(f"开始执行代码编写: {project_path}")
        self.logger.info(f"开始执行代码编写: {project_path}")
        
        # 检查项目结构
        if not ProjectManager.validate_project_structure(
            project_path, 
            required_dirs=['doc', 'plugin', 'cache'],
            required_files=['work.yaml']
        ):
            return False
        
        # 检查文档文件
        if not ProjectManager.check_documents(project_path):
            return False
        
        # 检查配置文件
        if not ProjectManager.validate_config(project_path):
            return False
        
        # 创建Agent并执行代码编写
        if not self._compose_code(project_path):
            return False
        
        terminal.success("代码编写完成！")
        self.logger.info("代码编写完成")
        # 注意：文件列表已由WorkflowManager在执行完成时打印，此处不再重复打印
        
        return True
    
    def _compose_code(self, project_path: str) -> bool:
        """执行代码编写"""
        try:
            terminal.info("正在启动AI Agent...")
            self.logger.info("启动AI Agent")
            
            # 创建Agent实例
            agent = Doc2PluginAgent(project_path, action='compose')
            
            # 加载配置
            if not agent.load_config():
                terminal.error("加载配置失败")
                self.logger.error("加载配置失败")
                return False
            
            # 初始化LLM和工具
            if not agent.initialize_llm():
                terminal.error("初始化LLM失败")
                self.logger.error("初始化LLM失败")
                return False
                
            if not agent.initialize_tools():
                terminal.error("初始化工具失败")
                self.logger.error("初始化工具失败")
                return False
            
            # 执行工作流
            terminal.info("开始执行工作流")
            self.logger.info("开始执行工作流")
            success = agent.execute_workflow()
            
            if success:
                terminal.success("AI Agent执行完成")
                self.logger.info("AI Agent执行完成")
                return True
            else:
                terminal.error("AI Agent执行失败")
                self.logger.error("AI Agent执行失败")
                return False
                
        except Exception as e:
            terminal.error(f"执行代码编写时发生错误: {e}")
            self.logger.error(f"执行代码编写时发生错误: {e}")
            traceback.print_exc()
            return False
