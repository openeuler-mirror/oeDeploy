"""
项目管理器 - 项目结构验证和文件检查

提供项目结构验证、配置验证、文档检查等公共功能。
"""

import os
import yaml
import logging
from typing import List, Tuple, Optional
from doc2plugin.utils.terminal_output import terminal


logger = logging.getLogger(__name__)


class ProjectManager:
    """项目管理器 - 提供项目相关的公共静态方法"""
    
    @staticmethod
    def validate_project_structure(project_path: str, required_dirs: List[str], 
                                   required_files: List[str]) -> bool:
        """
        验证项目结构
        
        Args:
            project_path: 项目路径
            required_dirs: 必需的目录列表
            required_files: 必需的文件列表
            
        Returns:
            bool: 验证通过返回True，否则返回False
        """
        logger.info(f"验证项目结构: {project_path}")
        
        if not os.path.exists(project_path):
            terminal.error(f"项目目录不存在: {project_path}")
            return False
        
        # 检查必要目录
        for directory in required_dirs:
            dir_path = os.path.join(project_path, directory)
            if not os.path.exists(dir_path):
                terminal.warning(f"目录不存在，正在创建: {directory}/")
                logger.info(f"创建目录: {dir_path}")
                try:
                    os.makedirs(dir_path)
                except Exception as e:
                    error_msg = f"无法创建目录 {directory}: {e}"
                    terminal.error(error_msg)
                    logger.error(error_msg)
                    return False
        
        # 检查必要文件
        for file_name in required_files:
            file_path = os.path.join(project_path, file_name)
            if not os.path.exists(file_path):
                terminal.error(f"配置文件不存在: {file_name}")
                terminal.info("请先运行 'doc2plugin init' 初始化项目")
                logger.error(f"配置文件不存在: {file_path}")
                return False
        
        logger.info("项目结构验证通过")
        return True
    
    @staticmethod
    def check_documents(project_path: str, doc_extensions: Tuple[str, ...] = ('.txt', '.md')) -> bool:
        """
        检查文档文件
        
        Args:
            project_path: 项目路径
            doc_extensions: 文档文件扩展名元组
            
        Returns:
            bool: 检查通过返回True，否则返回False
        """
        doc_dir = os.path.join(project_path, 'doc')
        logger.info(f"检查文档文件: {doc_dir}")
        
        if not os.path.exists(doc_dir):
            terminal.error("doc/ 目录不存在")
            logger.error(f"doc/ 目录不存在: {doc_dir}")
            return False
        
        # 获取文档文件列表
        doc_files = []
        for root, dirs, files in os.walk(doc_dir):
            for file in files:
                if file.endswith(doc_extensions):
                    doc_files.append(os.path.join(root, file))
        
        if not doc_files:
            terminal.warning("doc/ 目录中没有找到文档文件")
            terminal.info("将仅根据 work.yaml 中的任务要求继续执行")
            logger.warning("doc/ 目录为空，将使用任务描述继续")
            return True  # 允许在没有文档的情况下继续执行
        
        terminal.info(f"找到 {len(doc_files)} 个文档文件")
        logger.info(f"找到 {len(doc_files)} 个文档文件")
        for doc_file in doc_files:
            rel_path = os.path.relpath(doc_file, project_path)
            terminal.info(f"  - {rel_path}")
            logger.info(f"  - {rel_path}")
        
        return True
    
    @staticmethod
    def check_plugin_files(project_path: str) -> bool:
        """
        检查plugin目录是否包含已生成的文件
        
        Args:
            project_path: 项目路径
            
        Returns:
            bool: 检查通过返回True，否则返回False
        """
        plugin_dir = os.path.join(project_path, 'plugin')
        logger.info(f"检查plugin文件: {plugin_dir}")
        
        if not os.path.exists(plugin_dir):
            terminal.error("plugin/ 目录不存在")
            logger.error(f"plugin/ 目录不存在: {plugin_dir}")
            return False
        
        # 获取plugin目录中的文件列表
        plugin_files = []
        for root, dirs, files in os.walk(plugin_dir):
            for file in files:
                plugin_files.append(os.path.join(root, file))
        
        if not plugin_files:
            terminal.error("plugin/ 目录中没有找到已生成的文件")
            terminal.info("请先运行 'doc2plugin compose' 生成代码")
            logger.error("plugin/ 目录为空")
            return False
        
        terminal.info(f"找到 {len(plugin_files)} 个已生成的文件")
        logger.info(f"找到 {len(plugin_files)} 个已生成的文件")
        for plugin_file in plugin_files:
            rel_path = os.path.relpath(plugin_file, project_path)
            terminal.info(f"  - {rel_path}")
            logger.info(f"  - {rel_path}")
        
        return True
    
    @staticmethod
    def check_test_artifacts(project_path: str) -> bool:
        """
        检查测试产物（测试脚本和日志）是否存在
        
        Args:
            project_path: 项目路径
            
        Returns:
            bool: 检查通过返回True，否则返回False
        """
        cache_dir = os.path.join(project_path, 'cache')
        test_script = os.path.join(cache_dir, 'test.sh')
        test_log = os.path.join(cache_dir, 'test.log')
        
        logger.info(f"检查测试产物: {cache_dir}")
        
        if not os.path.exists(test_script):
            terminal.error("测试脚本不存在: cache/test.sh")
            terminal.info("请先运行 'doc2plugin test' 生成测试脚本")
            logger.error(f"测试脚本不存在: {test_script}")
            return False
        
        if not os.path.exists(test_log):
            terminal.error("测试日志不存在: cache/test.log")
            terminal.info("请先运行 'doc2plugin test' 执行测试并生成日志")
            logger.error(f"测试日志不存在: {test_log}")
            return False
        
        terminal.info("测试脚本和日志文件已找到")
        logger.info(f"测试脚本: {test_script}")
        logger.info(f"测试日志: {test_log}")
        
        return True
    
    @staticmethod
    def validate_config(project_path: str) -> bool:
        """
        验证配置文件
        
        Args:
            project_path: 项目路径
            
        Returns:
            bool: 验证通过返回True，否则返回False
        """
        config_path = os.path.join(project_path, 'work.yaml')
        logger.info(f"验证配置文件: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 检查必要的配置项
            if 'llm_info' not in config:
                terminal.error("配置文件缺少 llm_info 部分")
                logger.error("配置文件缺少 llm_info 部分")
                return False
            
            if 'task' not in config:
                terminal.error("配置文件缺少 task 部分")
                logger.error("配置文件缺少 task 部分")
                return False
            
            # 检查LLM配置
            llm_info = config['llm_info']
            required_llm_keys = ['base_url', 'api_key', 'model_name']
            for key in required_llm_keys:
                if key not in llm_info or not llm_info[key]:
                    terminal.error(f"LLM配置缺少或为空: {key}")
                    logger.error(f"LLM配置缺少或为空: {key}")
                    return False
            
            # 检查API密钥是否为默认值
            if llm_info['api_key'] == 'your-api-key-here':
                terminal.error("请在 work.yaml 中设置正确的 API 密钥")
                logger.error("API密钥未设置")
                return False
            
            # 检查任务配置
            task_info = config['task']
            if 'target' not in task_info or not task_info['target']:
                terminal.error("任务配置缺少目标描述 (target)")
                logger.error("任务配置缺少目标描述 (target)")
                return False
            
            if task_info['target'] == '请描述您的部署目标，例如：根据文档编写Nginx部署脚本':
                terminal.error("请在 work.yaml 中设置具体的任务目标")
                logger.error("任务目标未设置")
                return False
            
            terminal.info("配置文件验证通过")
            logger.info("配置文件验证通过")
            return True
            
        except yaml.YAMLError as e:
            terminal.error(f"配置文件格式错误: {e}")
            logger.error(f"配置文件格式错误: {e}")
            return False
        except Exception as e:
            terminal.error(f"读取配置文件时发生错误: {e}")
            logger.error(f"读取配置文件时发生错误: {e}")
            return False
