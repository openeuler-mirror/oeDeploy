"""
测试命令 - 执行已生成代码的测试流程

该命令启动AI Agent，根据配置文件和已生成的代码生成测试脚本并执行，
验证生成的代码是否符合预期功能。
"""

import os
import traceback
import subprocess
from doc2plugin.commands.base_command import BaseCommand
from doc2plugin.utils.terminal_output import terminal
from doc2plugin.utils.project_manager import ProjectManager
from doc2plugin.utils.agent_logger import setup_agent_logger, get_agent_logger
from doc2plugin.agent.core import Doc2PluginAgent


class TestCommand(BaseCommand):
    """测试命令 - 执行测试流程"""
    
    def __init__(self):
        """初始化test命令"""
        super().__init__()
        self.logger = None
    
    def execute(self, project_path: str) -> bool:
        """
        执行测试命令
        
        Args:
            project_path: 项目路径
            
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        # 设置agent日志记录器
        setup_agent_logger(project_path)
        self.logger = get_agent_logger()
        
        terminal.info(f"开始执行测试: {project_path}")
        self.logger.info(f"开始执行测试: {project_path}")
        
        # 检查项目结构
        if not ProjectManager.validate_project_structure(
            project_path,
            required_dirs=['plugin', 'cache'],
            required_files=['work.yaml']
        ):
            return False
        
        # 检查plugin目录是否有文件
        if not ProjectManager.check_plugin_files(project_path):
            return False
        
        # 检查配置文件
        if not ProjectManager.validate_config(project_path):
            return False
        
        # 生成测试脚本
        if not self._generate_test_script(project_path):
            return False
        
        # 执行测试脚本
        if not self._execute_test_script(project_path):
            return False
        
        terminal.success("测试完成！")
        self.logger.info("测试完成")
        
        return True
    
    def _generate_test_script(self, project_path: str) -> bool:
        """生成测试脚本"""
        try:
            test_script_path = os.path.join(project_path, 'cache', 'test.sh')
            test_log_path = os.path.join(project_path, 'cache', 'test.log')
            
            # 检查test.sh和test.log是否同时存在
            if os.path.exists(test_script_path) and os.path.exists(test_log_path):
                terminal.info("检测到已存在的测试脚本和测试日志，跳过生成步骤")
                self.logger.info("test.sh和test.log已存在，跳过生成测试脚本")
                terminal.info(f"测试脚本路径: {test_script_path}")
                self.logger.info(f"使用现有测试脚本: {test_script_path}")
                return True
            
            terminal.info("正在启动AI Agent生成测试脚本...")
            self.logger.info("启动AI Agent生成测试脚本")
            
            # 创建Agent实例
            agent = Doc2PluginAgent(project_path, action='test')
            
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
            
            # 执行测试脚本生成工作流
            terminal.info("开始生成测试脚本")
            self.logger.info("开始生成测试脚本")
            success = agent.execute_test_workflow()
            
            if success:
                terminal.success("测试脚本生成完成")
                self.logger.info("测试脚本生成完成")
                if os.path.exists(test_script_path):
                    terminal.info(f"测试脚本路径: {test_script_path}")
                    self.logger.info(f"测试脚本路径: {test_script_path}")
                return True
            else:
                terminal.error("测试脚本生成失败")
                self.logger.error("测试脚本生成失败")
                return False
                
        except Exception as e:
            terminal.error(f"生成测试脚本时发生错误: {e}")
            self.logger.error(f"生成测试脚本时发生错误: {e}")
            traceback.print_exc()
            return False
    
    def _execute_test_script(self, project_path: str) -> bool:
        """执行测试脚本"""
        test_script_path = os.path.join(project_path, 'cache', 'test.sh')
        test_log_path = os.path.join(project_path, 'cache', 'test.log')
        
        if not os.path.exists(test_script_path):
            terminal.error(f"测试脚本不存在: {test_script_path}")
            self.logger.error(f"测试脚本不存在: {test_script_path}")
            return False
        
        try:
            terminal.info("正在执行测试脚本...")
            self.logger.info("执行测试脚本")
            
            # 赋予测试脚本执行权限
            os.chmod(test_script_path, 0o755)
            self.logger.info(f"设置执行权限: {test_script_path}")
            
            # 执行测试脚本，并将输出重定向到test.log
            with open(test_log_path, 'w', encoding='utf-8') as log_file:
                result = subprocess.run(
                    ['bash', test_script_path],
                    cwd=project_path,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            
            self.logger.info(f"测试脚本执行完成，返回值: {result.returncode}")
            
            # 检查返回值
            if result.returncode == 0:
                terminal.success(f"测试通过（返回值: {result.returncode}）")
                terminal.info(f"完整日志: {test_log_path}")
                self.logger.info(f"测试通过，返回值: {result.returncode}")
                return True
            else:
                terminal.error(f"测试失败（返回值: {result.returncode}）")
                terminal.info(f"完整日志: {test_log_path}")
                self.logger.error(f"测试失败，返回值: {result.returncode}")
                return False
                
        except Exception as e:
            terminal.error(f"执行测试脚本时发生错误: {e}")
            self.logger.error(f"执行测试脚本时发生错误: {e}")
            traceback.print_exc()
            return False
