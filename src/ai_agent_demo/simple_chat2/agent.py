"""Agent class implementation with checkpoint-based conversation history."""

import uuid

from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from .state import SimpleChatState

DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."


class SimpleChatAgent:
    """LangGraph agent with checkpoint-based conversation history.

    Encapsulates model configuration, graph structure, and checkpoint mechanism
    using the Agent class pattern.

    Attributes:
        system_prompt: System message for the agent
        model: ChatOpenAI instance for LLM interactions
        config: RunnableConfig with unique thread_id for checkpoint isolation
        graph: Compiled LangGraph with InMemorySaver checkpoint support
    """

    def __init__(
        self,
        model_name: str = "gpt-5-nano",
        streaming: bool = True,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ):
        """Initialize agent with model and checkpoint configuration.

        Args:
            model_name: OpenAI model name (default: "gpt-5-nano")
            streaming: Enable token streaming (default: True)
            system_prompt: System message for the agent (default: helpful assistant)
        """
        self.system_prompt = system_prompt
        self.config = RunnableConfig(configurable={"thread_id": str(uuid.uuid4())})
        self.model = ChatOpenAI(model=model_name, streaming=streaming)
        self.graph = self._build_graph()

    def _build_graph(self):
        """Construct and compile the LangGraph with checkpoint support.

        Returns:
            Compiled LangGraph with InMemorySaver checkpoint mechanism
        """
        graph = StateGraph(SimpleChatState)
        graph.add_node(self.call_llm)
        graph.add_edge(START, self.call_llm.__name__)
        graph.add_edge(self.call_llm.__name__, END)

        checkpointer = InMemorySaver()
        return graph.compile(checkpointer=checkpointer)

    async def call_llm(self, state: SimpleChatState) -> dict:
        """Node function that invokes LLM with conversation history.

        Initializes SystemMessage on first call, appends user message,
        invokes LLM, and appends AI response to history.

        Args:
            state: Current state with user_request and chat_history

        Returns:
            Dict with updated chat_history for state merge
        """
        if state.chat_history is None:
            state.chat_history = [SystemMessage(self.system_prompt)]
        state.chat_history.append(HumanMessage(state.user_request))
        response: AIMessage = await self.model.ainvoke(state.chat_history)
        state.chat_history.append(response)
        update_field = {SimpleChatState.CHAT_HISTORY: state.chat_history}
        return update_field
