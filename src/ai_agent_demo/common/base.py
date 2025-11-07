"""Base classes for LangGraph agents."""

import uuid
from abc import ABC, abstractmethod

from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph


class AgentBase(ABC):
    """Base class for LangGraph agents.

    Args:
        **model_kwargs: Parameters passed to ChatOpenAI (model, streaming, max_tokens, etc.).
    """

    def __init__(self, **model_kwargs):
        # create model
        model_kwargs.setdefault("model", "gpt-5-nano")
        model_kwargs.setdefault("streaming", True)
        self.model = ChatOpenAI(**model_kwargs)

        # create config
        self.config = RunnableConfig(configurable={"thread_id": str(uuid.uuid4)})

        # build graph
        self.graph: CompiledStateGraph = self._build_graph()

    @abstractmethod
    def _build_graph(self) -> CompiledStateGraph:
        """Build and return the agent's state graph."""
        ...
