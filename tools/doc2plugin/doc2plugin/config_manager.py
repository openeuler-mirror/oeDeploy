"""
配置管理器模块 - 文档驱动的配置管理

该模块负责管理 work.yaml 和 modes.yaml 配置文件的读取和处理，
实现文档驱动的开发模式管理。

主要功能：
1. 读取和验证 work.yaml 配置文件
2. 读取 modes.yaml 模式配置文件
3. 根据模式自动加载对应的开发文档
4. 提供结构化的配置数据给不同的组件
5. 支持配置的扩展和定制

work.yaml 配置文件示例：
```yaml
# LLM 服务配置
llm_info:
  base_url: "https://api.deepseek.com/v1"    # LLM API 地址
  api_key: "your-api-key-here"             # API 密钥
  model_name: "deepseek-chat"              # 模型名称
  timeout: 600                             # 超时时间（秒）
  temperature: 0.1                         # 生成温度（0.0-2.0）
  max_tokens: null                         # 最大令牌数，null表示不限制
  max_llm_retries: 3                       # LLM调用最大重试次数
  llm_retry_delay: 1.0                     # 重试延迟（秒），使用指数退避策略

# 任务配置
task:
  target: "根据文档编写Nginx部署脚本，支持install和uninstall模式"  # 任务目标描述
  prompt: "部署环境为openEuler，假设拥有sudo权限"                    # 环境约束和技术要求
  mode: "shell"                                                     # 模式类型: shell 或 oedp
```

支持的配置字段说明：

llm_info（必需）:
- base_url: LLM API 服务地址
- api_key: API 访问密钥
- model_name: 使用的模型名称
- timeout: 请求超时时间，默认 600 秒
- temperature: 生成温度，默认 0.1，范围 0.0-2.0
- max_tokens: 最大生成令牌数，默认 None（不限制）
- max_llm_retries: LLM调用最大重试次数，默认 3 次
- llm_retry_delay: 重试延迟（秒），使用指数退避策略，默认 1.0 秒

task（必需）:
- target: 任务目标的详细描述
- prompt: 环境约束、技术要求等补充信息，默认为空
- mode: 模式类型，支持 "shell"（Shell脚本）和 "oedp"（oeDeploy插件）等

文档驱动设计：
- modes.yaml 定义了不同模式及其对应的开发文档路径
- 配置管理器会自动加载对应模式的开发文档
- 开发文档内容会传递给 LLM，作为项目开发的指导
- 这种设计使得添加新模式变得极其简单，无需修改代码
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ModeType(Enum):
    """模式类型枚举 - 支持 shell（硬编码）和其他文档驱动的模式"""
    SHELL = "shell"
    OEDP = "oedp"
    # 可扩展：将来添加新模式只需在这里添加枚举值


@dataclass
class LLMConfig:
    """LLM 配置数据类"""
    base_url: str
    api_key: str
    model_name: str
    timeout: int = 600
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    max_llm_retries: int = 3  # LLM调用最大重试次数
    llm_retry_delay: float = 1.0  # 重试延迟（秒），使用指数退避


@dataclass
class TaskConfig:
    """任务配置数据类"""
    target: str
    prompt: str = ""
    mode: ModeType = ModeType.SHELL


@dataclass
class LLMContextConfig:
    """传递给 LLM 的上下文配置"""
    target: str
    prompt: str
    mode: str
    develop_doc_content: Optional[str] = None  # 开发文档内容（文档驱动的核心）
    mode_prompt: Optional[List[str]] = None  # 模式专用提示词（高优先级）
    # 额外的上下文信息
    extra_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra_context is None:
            self.extra_context = {}
        if self.mode_prompt is None:
            self.mode_prompt = []


class ConfigManager:
    """
    配置管理器
    
    负责读取 work.yaml 配置文件，并根据不同的工作模式
    控制传递给 LLM 的配置信息。
    """
    
    def __init__(self, project_path: str, logger: Optional[logging.Logger] = None):
        """
        初始化配置管理器
        
        Args:
            project_path: 项目路径
            logger: 日志记录器
        """
        self.project_path = project_path
        self.logger = logger or logging.getLogger(__name__)
        self.raw_config: Optional[Dict[str, Any]] = None
        self.llm_config: Optional[LLMConfig] = None
        self.task_config: Optional[TaskConfig] = None
        self.modes_config: Optional[Dict[str, Any]] = None  # 模式配置
        self.develop_doc_content: Optional[str] = None  # 开发文档内容
        self.mode_prompt: Optional[List[str]] = None  # 模式专用提示词
        
        # 加载模式配置文件
        self._load_modes_config()
    
    def _load_modes_config(self):
        """加载模式配置文件 (modes.yaml)"""
        try:
            # modes.yaml 位于config目录
            modes_path_candidates = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'modes.yaml'),  # config目录
                os.path.join(self.project_path, 'config', 'modes.yaml'),  # 项目目录下的config
            ]
            
            modes_path = None
            for path in modes_path_candidates:
                if os.path.exists(path):
                    modes_path = path
                    break
            
            if not modes_path:
                self.logger.warning("未找到 modes.yaml 配置文件，将使用默认配置")
                self.modes_config = {
                    'shell': {'doc_path': None},
                    'oedp': {'doc_path': 'doc/DevelopInstruction.md'}
                }
                return
            
            with open(modes_path, 'r', encoding='utf-8') as f:
                self.modes_config = yaml.safe_load(f)
            
            self.logger.info(f"模式配置文件加载成功: {modes_path}")
            
        except Exception as e:
            self.logger.error(f"加载模式配置文件时发生错误: {e}")
            # 使用默认配置
            self.modes_config = {
                'shell': {'doc_path': None},
                'oedp': {'doc_path': 'doc/DevelopInstruction.md'}
            }
    
    def _load_develop_doc(self, mode: str, action: str = 'compose') -> bool:
        """
        加载指定模式和操作的开发文档和专用提示词（支持多个文档）
        
        Args:
            mode: 模式名称（如 'oedp'）
            action: 操作名称（如 'compose', 'test'）
            
        Returns:
            bool: 加载成功返回True，失败返回False
        """
        if mode == 'shell':
            # shell 模式不需要开发文档，但可能有专用提示词
            self.develop_doc_content = None
            self._load_mode_prompt(mode, action)
            self.logger.info(f"模式 '{mode}' 操作 '{action}' 不需要开发文档")
            return True
        
        if not self.modes_config or mode not in self.modes_config:
            self.logger.error(f"未找到模式 '{mode}' 的配置")
            return False
        
        mode_config = self.modes_config[mode]
        
        if action not in mode_config:
            self.logger.error(f"模式 '{mode}' 未配置操作 '{action}'")
            return False
        
        action_config = mode_config[action]
        doc_path = action_config.get('doc_path')
        
        if not doc_path:
            self.logger.error(f"模式 '{mode}' 操作 '{action}' 未配置开发文档路径")
            return False
        
        # 支持单个文档路径（字符串）或多个文档路径（列表）
        doc_paths = doc_path if isinstance(doc_path, list) else [doc_path]
        self.logger.info(f"模式 '{mode}' 操作 '{action}' 配置了 {len(doc_paths)} 个开发文档")
        
        loaded_contents = []
        loaded_files = []
        failed_files = []
        
        try:
            for idx, doc_path_item in enumerate(doc_paths, 1):
                # 清理路径（去除可能的空格和引号）
                doc_path_item = doc_path_item.strip().strip('"').strip("'")
                
                # 尝试多个路径候选位置
                doc_path_candidates = [
                    doc_path_item,  # 原始路径
                    os.path.join(os.path.dirname(os.path.dirname(__file__)), doc_path_item),  # 相对于包根目录
                    os.path.join(self.project_path, doc_path_item),  # 相对于项目目录
                ]
                
                doc_full_path = None
                for path in doc_path_candidates:
                    if os.path.exists(path):
                        doc_full_path = path
                        break
                
                if not doc_full_path:
                    self.logger.warning(f"未找到开发文档 [{idx}/{len(doc_paths)}]: {doc_path_item}")
                    failed_files.append(doc_path_item)
                    continue
                
                try:
                    with open(doc_full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    loaded_contents.append(content)
                    loaded_files.append(doc_full_path)
                    self.logger.info(f"开发文档 [{idx}/{len(doc_paths)}] 加载成功: {doc_full_path} (长度: {len(content)} 字符)")
                    
                except Exception as e:
                    self.logger.error(f"读取开发文档 [{idx}/{len(doc_paths)}] 时发生错误: {doc_path_item}, 错误: {e}")
                    failed_files.append(doc_path_item)
            
            # 检查是否至少加载了一个文档
            if not loaded_contents:
                self.logger.error(f"模式 '{mode}' 操作 '{action}' 的所有开发文档加载失败")
                return False
            
            # 合并所有文档内容，使用分隔符区分不同文档
            separator = "\n\n" + "=" * 80 + "\n"
            doc_separator = "\n" + "-" * 80 + "\n"
            
            merged_content_parts = []
            for idx, (content, file_path) in enumerate(zip(loaded_contents, loaded_files), 1):
                file_name = os.path.basename(file_path)
                merged_content_parts.append(
                    f"## 文档 {idx}: {file_name}\n{doc_separator}{content}"
                )
            
            self.develop_doc_content = separator.join(merged_content_parts)
            
            # 记录加载摘要
            total_chars = sum(len(c) for c in loaded_contents)
            self.logger.info(
                f"模式 '{mode}' 操作 '{action}' 开发文档加载完成: "
                f"成功 {len(loaded_contents)}/{len(doc_paths)} 个文档, "
                f"总长度 {total_chars} 字符"
            )
            
            if failed_files:
                self.logger.warning(f"以下文档加载失败: {', '.join(failed_files)}")
            
            # 加载模式专用提示词
            self._load_mode_prompt(mode, action)
            
            return True
            
        except Exception as e:
            self.logger.error(f"加载开发文档时发生错误: {e}")
            return False
    
    def _load_mode_prompt(self, mode: str, action: str = 'compose'):
        """
        加载指定模式和操作的专用提示词
        
        Args:
            mode: 模式名称（如 'oedp', 'shell'）
            action: 操作名称（如 'compose', 'test'）
        """
        if not self.modes_config or mode not in self.modes_config:
            self.logger.info(f"模式 '{mode}' 没有配置专用提示词")
            self.mode_prompt = None
            return
        
        mode_config = self.modes_config[mode]
        
        if action not in mode_config:
            self.logger.info(f"模式 '{mode}' 操作 '{action}' 没有配置专用提示词")
            self.mode_prompt = None
            return
        
        action_config = mode_config[action]
        prompt = action_config.get('prompt')
        
        if not prompt:
            self.logger.info(f"模式 '{mode}' 操作 '{action}' 没有配置专用提示词")
            self.mode_prompt = None
            return
        
        # prompt 可以是字符串或列表
        if isinstance(prompt, str):
            self.mode_prompt = [prompt]
        elif isinstance(prompt, list):
            self.mode_prompt = prompt
        else:
            self.logger.warning(f"模式 '{mode}' 操作 '{action}' 的 prompt 字段格式不正确（应该是字符串或列表）")
            self.mode_prompt = None
            return
        
        self.logger.info(f"模式 '{mode}' 操作 '{action}' 专用提示词加载成功: {len(self.mode_prompt)} 条提示")
        for idx, p in enumerate(self.mode_prompt, 1):
            self.logger.info(f"  提示 {idx}: {p[:50]}..." if len(p) > 50 else f"  提示 {idx}: {p}")
    
    def load_config(self, action: str = 'compose') -> bool:
        """
        加载项目配置文件 (work.yaml)
        
        Args:
            action: 操作类型，如 'compose', 'test', 'modify'，默认为 'compose'
        
        Returns:
            bool: 加载成功返回True，失败返回False
        """
        config_path = os.path.join(self.project_path, 'work.yaml')
        
        if not os.path.exists(config_path):
            self.logger.error(f"配置文件不存在: {config_path}")
            return False
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.raw_config = yaml.safe_load(f)
            
            # 验证和解析配置
            if not self._validate_config():
                return False
            
            if not self._parse_config(action):
                return False
            
            self.logger.info("配置文件加载成功")
            return True
            
        except yaml.YAMLError as e:
            self.logger.error(f"配置文件格式错误: {e}")
            return False
        except Exception as e:
            self.logger.error(f"加载配置文件时发生错误: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """验证配置文件的必要字段"""
        if not self.raw_config:
            self.logger.error("配置文件为空")
            return False
        
        # 验证必要的配置项
        required_keys = ['llm_info', 'task']
        for key in required_keys:
            if key not in self.raw_config:
                self.logger.error(f"配置文件缺少必要字段: {key}")
                return False
        
        # 验证LLM配置
        llm_required = ['base_url', 'api_key', 'model_name']
        for key in llm_required:
            if key not in self.raw_config['llm_info']:
                self.logger.error(f"LLM配置缺少必要字段: {key}")
                return False
        
        # 验证任务配置
        task_required = ['target', 'mode']
        for key in task_required:
            if key not in self.raw_config['task']:
                self.logger.error(f"任务配置缺少必要字段: {key}")
                return False
        
        return True
    
    def _parse_config(self, action: str = 'compose') -> bool:
        """
        解析配置文件到结构化数据
        
        Args:
            action: 操作类型，如 'compose', 'test', 'modify'
        """
        try:
            # 解析 LLM 配置
            llm_info = self.raw_config['llm_info']
            self.llm_config = LLMConfig(
                base_url=llm_info['base_url'],
                api_key=llm_info['api_key'],
                model_name=llm_info['model_name'],
                timeout=llm_info.get('timeout', 600),
                temperature=llm_info.get('temperature', 0.1),
                max_tokens=llm_info.get('max_tokens', None),
                max_llm_retries=llm_info.get('max_llm_retries', 3),
                llm_retry_delay=llm_info.get('llm_retry_delay', 1.0)
            )
            
            # 解析任务配置
            task_info = self.raw_config['task']
            mode_str = task_info['mode'].lower()
            try:
                mode_type = ModeType(mode_str)
            except ValueError:
                self.logger.error(f"不支持的模式类型: {mode_str}")
                return False
            
            self.task_config = TaskConfig(
                target=task_info['target'],
                prompt=task_info.get('prompt', ''),
                mode=mode_type
            )
            
            # 加载指定操作的开发文档和提示词
            if not self._load_develop_doc(mode_str, action):
                if mode_str != 'shell':  # shell 模式不需要开发文档
                    self.logger.error(f"加载模式 '{mode_str}' {action}操作的开发文档失败")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"解析配置文件时发生错误: {e}")
            return False
    
    def get_llm_config(self) -> Optional[LLMConfig]:
        """获取 LLM 配置"""
        return self.llm_config
    
    def get_task_config(self) -> Optional[TaskConfig]:
        """获取任务配置"""
        return self.task_config
    
    def get_raw_config(self) -> Optional[Dict[str, Any]]:
        """获取原始配置"""
        return self.raw_config
    
    def get_llm_context_config(self, 
                              extra_context: Optional[Dict[str, Any]] = None) -> LLMContextConfig:
        """
        获取传递给 LLM 的上下文配置
        
        这个方法根据不同的需求，控制传递给 LLM 的配置信息。
        核心改进：将开发文档内容注入到上下文中，实现文档驱动。
        
        Args:
            extra_context: 额外的上下文信息
            
        Returns:
            LLMContextConfig: 结构化的 LLM 上下文配置
        """
        if not self.task_config:
            raise ValueError("配置未正确加载")
        
        # 基础上下文信息
        context_extra = extra_context or {}
        
        return LLMContextConfig(
            target=self.task_config.target,
            prompt=self.task_config.prompt,
            mode=self.task_config.mode.value,
            develop_doc_content=self.develop_doc_content,  # 核心：传递开发文档内容
            mode_prompt=self.mode_prompt,  # 模式专用提示词（高优先级）
            extra_context=context_extra
        )
    
    def get_filtered_config_for_mode(self) -> Dict[str, Any]:
        """
        获取过滤后的配置信息
        
        Returns:
            Dict[str, Any]: 过滤后的配置信息
        """
        if not self.task_config:
            raise ValueError("配置未正确加载")
        
        return {
            'target': self.task_config.target,
            'prompt': self.task_config.prompt,
            'mode': self.task_config.mode.value
        }
    
    def validate_api_key(self) -> bool:
        """验证 API 密钥是否有效（不是默认值）"""
        if not self.llm_config:
            return False
        
        invalid_keys = ['your-api-key-here', 'your-api-key', '']
        return self.llm_config.api_key not in invalid_keys
    
    def validate_task_target(self) -> bool:
        """验证任务目标是否有效（不是默认值）"""
        if not self.task_config:
            return False
        
        invalid_targets = [
            '请描述您的部署目标，例如：根据文档编写Nginx部署脚本',
            '请描述您的部署目标',
            ''
        ]
        return self.task_config.target not in invalid_targets
    
    def get_develop_doc_content(self) -> Optional[str]:
        """获取当前模式的开发文档内容"""
        return self.develop_doc_content
    
    def get_mode_prompt(self) -> Optional[List[str]]:
        """获取当前模式的专用提示词"""
        return self.mode_prompt
    
    def get_mode_config(self, mode: str) -> Optional[Dict[str, Any]]:
        """获取指定模式的配置信息"""
        if not self.modes_config:
            return None
        return self.modes_config.get(mode)
