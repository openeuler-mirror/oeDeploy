"""提示词管理器 - 使用 LangChain 的 ChatPromptTemplate"""

from typing import Optional, List
from langchain_core.messages import SystemMessage, HumanMessage

from doc2plugin.prompts.system_prompts import SystemPromptBuilder
from doc2plugin.prompts.document_prompts import DocumentPromptBuilder


class PromptManager:
    def __init__(self, develop_doc_content: Optional[str] = None, mode_prompt: Optional[List[str]] = None):
        self.system_builder = SystemPromptBuilder(develop_doc_content, mode_prompt or [])
        self.document_builder = DocumentPromptBuilder()
        self._cache = {}

    def get_system_prompt(self, mode: str = "shell") -> str:
        if mode not in self._cache:
            self._cache[mode] = self.system_builder.build_system_prompt(mode)
        return self._cache[mode]

    def format_messages(self, mode: str, human_message: str, **kwargs) -> List:
        if kwargs:
            try:
                human_message = human_message.format(**kwargs)
            except KeyError:
                pass
        return [SystemMessage(content=self.get_system_prompt(mode)), HumanMessage(content=human_message)]

    def get_document_refinement_prompt(self, task_target: str, task_prompt: str) -> str:
        return self.document_builder.build_document_refinement_prompt(task_target, task_prompt)
