"""任务提示词构建器 - 构建任务规划和执行相关的提示词"""

from doc2plugin.prompts.components import PromptComponents, PromptConfig


class TaskPromptBuilder:
    def __init__(self):
        self.components = PromptComponents()
        self.config = PromptConfig()

    def build_task_planning_prompt(self, target, prompt, mode, has_develop_doc=False):
        raise NotImplementedError

    def build_task_adjustment_prompt(self, current_tasks, issue_description):
        raise NotImplementedError

    def build_task_retry_prompt(self, task_name, error_message, retry_count):
        raise NotImplementedError

    def build_quality_check_prompt(self):
        raise NotImplementedError
