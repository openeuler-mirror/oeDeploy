"""
基于 LangGraph 的工作流系统 - 任务执行与编排

功能描述：
1. 基于 LangGraph 状态图管理工作流
2. Agent 自动选择和使用工具完成任务
3. 统一的任务执行器，负责分发不同类型的任务
4. 完整的上下文构建和管理

核心组件：
- LangGraphWorkflowManager: 工作流协调器
- AgentTaskExecutor: 任务执行器
- WorkflowState: 状态定义
"""

import os
import json
import uuid
from typing import Dict, Any, List, TypedDict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from langgraph.graph import StateGraph, END
from langchain_core.output_parsers import JsonOutputParser

from doc2plugin.utils.terminal_output import terminal
from doc2plugin.prompts.agent_prompts import AgentPromptTemplates


# ==================== 数据模型 ====================

class TaskType(Enum):
    """任务类型枚举"""
    ANALYSIS = "analysis"
    EXTRACTION = "extraction"
    GENERATION = "generation"
    VALIDATION = "validation"
    DIRECTORY_OPERATION = "dir_op"


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskResult:
    """任务执行结果"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    artifacts: Optional[List[str]] = None
    error: Optional[str] = None


@dataclass
class Task:
    """任务模型"""
    id: str
    name: str
    description: str
    task_type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = None
    parameters: Dict[str, Any] = None
    expected_outputs: List[str] = None
    max_retries: int = 3
    result: Optional[TaskResult] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.parameters is None:
            self.parameters = {}
        if self.expected_outputs is None:
            self.expected_outputs = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['task_type'] = self.task_type.value
        data['status'] = self.status.value
        return data


# ==================== LangGraph 状态定义 ====================

class WorkflowState(TypedDict):
    """工作流状态"""
    project_path: str
    mode: str
    
    doc_refined: bool
    file_manifest: Optional[Dict]
    
    tasks: List[Dict]
    completed_task_ids: List[str]
    current_task_id: Optional[str]
    
    generated_files: List[str]
    errors: List[str]
    
    workflow_complete: bool


# ==================== Agent 任务执行器 ====================

class AgentTaskExecutor:
    """
    任务执行器
    
    负责执行不同类型的任务（分析、提取、生成、验证、目录操作）
    """
    
    def __init__(self, project_path, llm_client, tools, prompts, config_manager, logger):
        self.project_path = project_path
        self.llm_client = llm_client
        self.tools = tools
        self.prompts = prompts
        self.config_manager = config_manager
        self.logger = logger
        
        self.json_parser = JsonOutputParser()
    
    def execute_task(self, task: Task) -> TaskResult:
        """执行任务 - 根据类型分发到不同的执行方法"""
        try:
            self.logger.info(f"执行任务: {task.name} ({task.task_type.value})")
            
            if task.task_type == TaskType.ANALYSIS:
                return self._execute_analysis(task)
            elif task.task_type == TaskType.EXTRACTION:
                return self._execute_extraction(task)
            elif task.task_type == TaskType.GENERATION:
                return self._execute_generation(task)
            elif task.task_type == TaskType.VALIDATION:
                return self._execute_validation(task)
            elif task.task_type == TaskType.DIRECTORY_OPERATION:
                return self._execute_dir_op(task)
            else:
                return TaskResult(
                    success=False,
                    message=f"不支持的任务类型: {task.task_type}",
                    error=f"Unsupported task type: {task.task_type}"
                )
        except Exception as e:
            self.logger.error(f"任务执行异常: {e}")
            return TaskResult(success=False, message="任务执行失败", error=str(e))
    
    def _execute_analysis(self, task: Task) -> TaskResult:
        """执行分析任务（文件清单生成）- 直接调用 LLM"""
        prompt = task.parameters.get('prompt', '')
        output_file = task.parameters.get('output_file')
        
        # 读取输入内容
        content = self._read_source_file()
        self.logger.info(f"读取输入内容: {len(content)} 字符")
        
        # 获取mode
        task_config = self.config_manager.get_task_config()
        mode = task_config.mode.value if task_config else 'shell'
        
        # 构建提示词
        human_prompt = AgentPromptTemplates.get_file_manifest_analysis_prompt(prompt, content)
        self.logger.info(f"构建文件清单分析提示词: {len(human_prompt)} 字符")
        
        # 调用 LLM
        messages = self.prompts.format_messages(mode, human_prompt)
        response = self.llm_client.invoke_with_streaming(
            messages,
            "正在分析...",
            stage=f"分析-{task.name}",
            output_parser=self.json_parser
        )
        
        # 保存结果
        if output_file:
            self._write_file(output_file, response)
            
            # 验证格式
            try:
                manifest = json.loads(response)
                if 'files' not in manifest:
                    return TaskResult(success=False, message="文件清单格式错误")
                self.logger.info(f"文件清单包含 {len(manifest['files'])} 个文件")
            except json.JSONDecodeError as e:
                return TaskResult(success=False, message="JSON格式错误", error=str(e))
        
        return TaskResult(
            success=True,
            message="分析完成",
            artifacts=[output_file] if output_file else []
        )
    
    def _execute_extraction(self, task: Task) -> TaskResult:
        """执行提取任务（文档提纯）- 直接调用 LLM"""
        prompt = task.parameters.get('prompt', '')
        input_files = task.parameters.get('input_files', [])
        output_file = task.parameters.get('output_file')
        mode = task.parameters.get('mode', 'shell')
        
        # 读取输入文件
        content = ""
        for file_path in input_files:
            full_path = os.path.join(self.project_path, file_path)
            if os.path.isdir(full_path):
                for item in os.listdir(full_path):
                    if item.endswith(('.md', '.txt')):
                        doc_path = os.path.join(file_path, item)
                        file_content = self._read_file(doc_path)
                        if file_content:
                            content += f"\n\n=== {doc_path} ===\n{file_content}\n"
        
        if not content.strip():
            content = "(未提供文档内容)"
        
        # 调用 LLM
        separator = "\n" + "="*80 + "\n"
        human_prompt = prompt + separator + "原始内容:" + separator + content + separator
        messages = self.prompts.format_messages(mode, human_prompt)
        
        response = self.llm_client.invoke_with_streaming(
            messages,
            "正在提取信息...",
            stage=f"提取-{task.name}"
        )
        
        # 保存结果
        if output_file:
            self._write_file(output_file, response)
        
        return TaskResult(
            success=True,
            message="提取完成",
            artifacts=[output_file] if output_file else []
        )
    
    def _execute_generation(self, task: Task) -> TaskResult:
        """执行生成任务 - 直接调用 LLM"""
        prompt = task.parameters.get('prompt', '')
        output_file = task.parameters.get('output_file')
        mode = task.parameters.get('mode', 'shell')
        
        # 构建完整上下文
        full_context = self._build_generation_context()
        self.logger.info(f"构建生成任务上下文: {len(full_context)} 字符")
        
        human_prompt = f"""{prompt}

{"=" * 80}
参考内容:
{"=" * 80}
{full_context}

{"=" * 80}
**重要：请以JSON格式返回，格式如下：**
{{"file_content": "实际的文件内容"}}

只返回纯JSON，不要添加任何解释。"""
        
        # 调用 LLM
        messages = self.prompts.format_messages(mode, human_prompt)
        response = self.llm_client.invoke_with_streaming(
            messages,
            "正在生成内容...",
            stage=f"生成-{task.name}"
        )
        
        # 提取 file_content
        generated_content = self._extract_file_content(response)
        
        # 写入文件
        if output_file:
            self._write_file(output_file, generated_content)
        
        return TaskResult(
            success=True,
            message="生成完成",
            artifacts=[output_file] if output_file else []
        )
    
    def _execute_validation(self, task: Task) -> TaskResult:
        """执行验证任务"""
        validation_type = task.parameters.get('validation_type')
        
        if validation_type == 'file_manifest':
            manifest_file = task.parameters.get('manifest_file', 'cache/file_manifest.json')
            manifest_path = os.path.join(self.project_path, manifest_file)
            
            if not os.path.exists(manifest_path):
                return TaskResult(success=False, message=f"文件清单不存在: {manifest_file}")
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            files = manifest.get('files', [])
            missing_files = []
            
            for file_info in files:
                file_path = file_info['path']
                full_path = os.path.join(self.project_path, file_path)
                if not os.path.exists(full_path):
                    missing_files.append(file_path)
            
            if missing_files:
                return TaskResult(
                    success=False,
                    message=f"以下 {len(missing_files)} 个文件未生成:\n" + "\n".join(f"  - {f}" for f in missing_files)
                )
            
            return TaskResult(
                success=True,
                message=f"✅ 所有 {len(files)} 个文件已按清单生成"
            )
        
        return TaskResult(success=True, message="验证完成")
    
    def _execute_dir_op(self, task: Task) -> TaskResult:
        """执行目录操作"""
        directories = task.parameters.get('directories', [])
        
        if not directories:
            return TaskResult(success=False, message="缺少directories参数")
        
        for directory in directories:
            full_path = os.path.join(self.project_path, directory)
            os.makedirs(full_path, exist_ok=True)
            self.logger.info(f"创建目录: {directory}")
        
        return TaskResult(
            success=True,
            message=f"成功创建 {len(directories)} 个目录",
            artifacts=directories
        )
    
    # ==================== 辅助方法 ====================
    
    def _build_generation_context(self) -> str:
        """构建生成任务的完整上下文"""
        context_parts = []
        
        # 1. 提纯后的文档
        source_content = self._read_source_file()
        context_parts.append(source_content)
        
        # 2. 文件清单
        manifest_content = self._read_file_manifest()
        if manifest_content:
            context_parts.append(manifest_content)
        
        # 3. 已生成的文件
        plugin_files_content = self._read_plugin_files()
        if plugin_files_content:
            context_parts.append(plugin_files_content)
        
        return "\n\n".join(context_parts)
    
    def _extract_file_content(self, response: str) -> str:
        """从LLM响应中提取文件内容"""
        try:
            # 清理可能的Markdown代码块
            cleaned = response.strip()
            if cleaned.startswith('```'):
                lines = cleaned.split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                cleaned = '\n'.join(lines).strip()
            
            data = json.loads(cleaned)
            if 'file_content' in data:
                return data['file_content']
            return response
        except:
            return response
    
    def _read_source_file(self) -> str:
        """读取提纯后的文档"""
        return self._read_file("cache/source.md") or "(未提供文档内容)"
    
    def _read_file_manifest(self) -> str:
        """读取并格式化文件清单"""
        manifest_path = os.path.join(self.project_path, 'cache/file_manifest.json')
        if not os.path.exists(manifest_path):
            self.logger.debug("文件清单不存在")
            return ""
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            self.logger.info(f"读取文件清单: {len(manifest.get('files', []))} 个文件")
            
            # 使用 ContextBuilder 来构建文件清单上下文，确保包含完整的 implementation 信息
            from doc2plugin.prompts.context_builder import ContextBuilder
            context_builder = ContextBuilder(self.project_path)
            
            # 提取所有文件路径作为 output_files
            output_files = [f.get('path', '') for f in manifest.get('files', [])]
            
            # 构建完整的文件清单上下文
            content = context_builder.build_manifest_context(manifest, output_files)
            
            return content
        except Exception as e:
            self.logger.error(f"读取文件清单失败: {e}")
            return ""
    
    def _read_plugin_files(self) -> str:
        """读取已生成的plugin文件"""
        plugin_dir = os.path.join(self.project_path, 'plugin')
        if not os.path.exists(plugin_dir):
            return ""
        
        content = "="*80 + "\n【已生成文件】\n" + "="*80 + "\n"
        
        file_contents = []
        for root, dirs, files in os.walk(plugin_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for filename in files:
                if filename.startswith('.'):
                    continue
                
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, self.project_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    file_contents.append(f"\n{rel_path}:\n{file_content}\n")
                except:
                    pass
        
        # 在文件内容之间添加分隔符
        content += ("\n" + "-"*60 + "\n").join(file_contents)
        
        return content
    
    def _read_file(self, file_path: str) -> str:
        """读取文件"""
        full_path = os.path.join(self.project_path, file_path)
        if not os.path.exists(full_path):
            return ""
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    
    def _write_file(self, file_path: str, content: str):
        """写入文件"""
        full_path = os.path.join(self.project_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"写入文件: {file_path}")


# ==================== LangGraph 工作流 ====================

class LangGraphWorkflowManager:
    """
    基于 LangGraph 的工作流管理器
    
    使用状态图来管理任务执行流程
    """
    
    def __init__(self, project_path, llm_client, tools, prompts, config_manager, logger):
        self.project_path = project_path
        self.llm_client = llm_client
        self.tools = tools
        self.prompts = prompts
        self.config_manager = config_manager
        self.logger = logger
        
        self.executor = AgentTaskExecutor(
            project_path, llm_client, tools, prompts, config_manager, logger
        )
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建状态图"""
        workflow = StateGraph(WorkflowState)
        
        # 添加节点
        workflow.add_node("refine_doc", self._refine_document)
        workflow.add_node("generate_manifest", self._generate_manifest)
        workflow.add_node("generate_tasks", self._generate_tasks_from_manifest)
        workflow.add_node("execute_task", self._execute_single_task)
        workflow.add_node("check_completion", self._check_completion)
        
        # 设置入口
        workflow.set_entry_point("refine_doc")
        
        # 添加边
        workflow.add_edge("refine_doc", "generate_manifest")
        workflow.add_edge("generate_manifest", "generate_tasks")
        workflow.add_edge("generate_tasks", "execute_task")
        workflow.add_conditional_edges(
            "execute_task",
            self._should_continue,
            {
                "continue": "execute_task",
                "check": "check_completion",
            }
        )
        workflow.add_edge("check_completion", END)
        
        return workflow.compile()
    
    def _tasks_from_state(self, tasks_data: List[Dict]) -> List[Task]:
        """从状态中的字典列表重建 Task 对象"""
        tasks = []
        for t in tasks_data:
            task_dict = t.copy()
            
            if isinstance(task_dict.get('task_type'), str):
                task_dict['task_type'] = TaskType(task_dict['task_type'])
            elif not isinstance(task_dict.get('task_type'), TaskType):
                task_dict['task_type'] = TaskType.GENERATION
            
            if isinstance(task_dict.get('status'), str):
                task_dict['status'] = TaskStatus(task_dict['status'])
            elif not isinstance(task_dict.get('status'), TaskStatus):
                task_dict['status'] = TaskStatus.PENDING
            
            try:
                tasks.append(Task(**task_dict))
            except Exception as e:
                self.logger.error(f"无法重建任务: {e}")
                continue
        
        return tasks
    
    def _should_continue(self, state: WorkflowState) -> str:
        """判断是否继续执行任务"""
        tasks = self._tasks_from_state(state["tasks"])
        completed_ids = set(state["completed_task_ids"])
        
        for task in tasks:
            if task.status == TaskStatus.PENDING:
                if all(dep in completed_ids for dep in task.dependencies):
                    return "continue"
        
        return "check"
    
    def _refine_document(self, state: WorkflowState) -> Dict:
        """文档提纯节点"""
        terminal.info("正在提纯文档...", 'process')
        self.logger.info("步骤0: 文档提纯")
        
        filtered_config = self.config_manager.get_filtered_config_for_mode()
        target = filtered_config.get('target', '')
        prompt_constraint = filtered_config.get('prompt', '')
        mode = filtered_config['mode']
        
        refinement_prompt = self.prompts.get_document_refinement_prompt(target, prompt_constraint)
        
        task = Task(
            id=str(uuid.uuid4()),
            name="refine_documents",
            task_type=TaskType.EXTRACTION,
            description="文档提纯",
            parameters={
                "prompt": refinement_prompt,
                "input_files": ["doc"],
                "output_file": "cache/source.md",
                "mode": mode
            },
            expected_outputs=["cache/source.md"]
        )
        
        result = self.executor.execute_task(task)
        
        if result.success:
            terminal.success("文档提纯完成", 'check')
            state["doc_refined"] = True
        else:
            terminal.error("文档提纯失败")
            state["errors"].append("文档提纯失败")
        
        return state
    
    def _generate_manifest(self, state: WorkflowState) -> Dict:
        """生成文件清单节点"""
        terminal.info("正在生成文件清单...", 'process')
        self.logger.info("步骤1: 生成文件清单")
        
        filtered_config = self.config_manager.get_filtered_config_for_mode()
        target = filtered_config.get('target', '')
        prompt_constraint = filtered_config.get('prompt', '')
        
        full_prompt = AgentPromptTemplates.get_file_manifest_task_prompt(target, prompt_constraint)
        
        task = Task(
            id=str(uuid.uuid4()),
            name="plan_file_structure",
            task_type=TaskType.ANALYSIS,
            description="生成文件清单",
            parameters={
                "prompt": full_prompt,
                "input_files": ["cache/source.md"],
                "output_file": "cache/file_manifest.json",
            },
            expected_outputs=["cache/file_manifest.json"]
        )
        
        result = self.executor.execute_task(task)
        
        if result.success:
            terminal.success("文件清单生成完成", 'check')
            manifest_path = os.path.join(self.project_path, "cache/file_manifest.json")
            with open(manifest_path, 'r', encoding='utf-8') as f:
                state["file_manifest"] = json.load(f)
        else:
            terminal.error("文件清单生成失败")
            state["errors"].append("文件清单生成失败")
        
        return state
    
    def _generate_tasks_from_manifest(self, state: WorkflowState) -> Dict:
        """从文件清单生成任务列表"""
        self.logger.info("步骤2: 根据文件清单生成任务")
        
        manifest = state.get("file_manifest")
        if not manifest:
            state["errors"].append("文件清单为空")
            return state
        
        filtered_config = self.config_manager.get_filtered_config_for_mode()
        target = filtered_config.get('target', '')
        prompt_constraint = filtered_config.get('prompt', '')
        mode = filtered_config['mode']
        
        tasks = []
        files = manifest.get('files', [])
        
        # 提取目录
        directories = set()
        for file_info in files:
            dir_path = os.path.dirname(file_info['path'])
            if dir_path:
                parts = dir_path.split('/')
                for i in range(1, len(parts) + 1):
                    directories.add('/'.join(parts[:i]))
        
        # 创建目录任务
        if directories:
            dir_task = Task(
                id="create_directories",
                name="创建目录结构",
                task_type=TaskType.DIRECTORY_OPERATION,
                description="创建项目目录",
                dependencies=[],
                parameters={"directories": sorted(directories)}
            )
            tasks.append(dir_task.to_dict())
        
        # 为每个文件创建生成任务
        for idx, file_info in enumerate(files, start=1):
            file_path = file_info['path']
            description = file_info.get('description', '')
            
            task_id = f"generate_file_{idx}"
            task_name = f"生成_{os.path.basename(file_path)}"
            
            dependencies = ["create_directories"] if directories else []
            
            generation_prompt = AgentPromptTemplates.get_file_generation_prompt(
                target, prompt_constraint, description
            )
            generation_prompt += f"\n\n生成文件: {file_path}"
            
            gen_task = Task(
                id=task_id,
                name=task_name,
                task_type=TaskType.GENERATION,
                description=f"{description}: {file_path}",
                dependencies=dependencies,
                parameters={
                    "prompt": generation_prompt,
                    "output_file": file_path,
                    "mode": mode
                }
            )
            tasks.append(gen_task.to_dict())
        
        # 验证任务
        validate_task = Task(
            id="validate_files",
            name="验证文件",
            task_type=TaskType.VALIDATION,
            description="验证所有文件生成",
            dependencies=[f"generate_file_{i}" for i in range(1, len(files) + 1)],
            parameters={
                "validation_type": "file_manifest",
                "manifest_file": "cache/file_manifest.json"
            }
        )
        tasks.append(validate_task.to_dict())
        
        state["tasks"] = tasks
        terminal.success(f"生成 {len(tasks)} 个任务", 'check')
        
        return state
    
    def _execute_single_task(self, state: WorkflowState) -> Dict:
        """执行单个任务节点"""
        tasks = self._tasks_from_state(state["tasks"])
        completed_ids = set(state["completed_task_ids"])
        
        # 找到下一个可执行的任务
        next_task = None
        for task in tasks:
            if task.status == TaskStatus.PENDING:
                if all(dep in completed_ids for dep in task.dependencies):
                    next_task = task
                    break
        
        if not next_task:
            state["workflow_complete"] = True
            return state
        
        # 执行任务
        terminal.info(f"正在执行: {next_task.name}", 'process')
        result = self.executor.execute_task(next_task)
        
        # 更新任务状态
        for i, t in enumerate(state["tasks"]):
            if t["id"] == next_task.id:
                if result.success:
                    state["tasks"][i]["status"] = TaskStatus.COMPLETED.value
                    state["completed_task_ids"].append(next_task.id)
                    terminal.success(f"任务完成: {next_task.name}", 'check')
                    
                    if result.artifacts:
                        state["generated_files"].extend(result.artifacts)
                else:
                    state["tasks"][i]["status"] = TaskStatus.FAILED.value
                    terminal.error(f"任务失败: {next_task.name}")
                    state["errors"].append(f"{next_task.name}: {result.message}")
                break
        
        return state
    
    def _check_completion(self, state: WorkflowState) -> Dict:
        """检查完成状态节点"""
        tasks = self._tasks_from_state(state["tasks"])
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)
        
        terminal.newline()
        terminal.info(f"✅ 工作流完成: 成功 {completed}/{len(tasks)}, 失败 {failed}", 'summary')
        
        if state["generated_files"]:
            for file in state["generated_files"]:
                if not file.startswith('cache/'):
                    terminal.success(f"  {file}", 'file')
        
        state["workflow_complete"] = True
        return state
    
    def execute_workflow(self) -> bool:
        """执行工作流"""
        initial_state = WorkflowState(
            project_path=self.project_path,
            mode=self.config_manager.get_task_config().mode.value,
            doc_refined=False,
            file_manifest=None,
            tasks=[],
            completed_task_ids=[],
            current_task_id=None,
            generated_files=[],
            errors=[],
            workflow_complete=False
        )
        
        try:
            final_state = self.graph.invoke(initial_state)
            return len(final_state["errors"]) == 0
        except Exception as e:
            self.logger.error(f"工作流执行失败: {e}")
            terminal.error(f"工作流执行失败: {e}")
            return False
    
    def execute_test_workflow(self) -> bool:
        """执行测试脚本生成工作流"""
        raise NotImplementedError("execute_test_workflow 尚未实现")
    
    def execute_modify_workflow(self) -> bool:
        """执行修改工作流程 - 基于测试结果修改代码"""
        raise NotImplementedError("execute_modify_workflow 尚未实现")
