"""Agent class implementation with checkpoint-based conversation history."""

from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ai_agent_demo.common import AgentBase

from .state import SimpleChatState

DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."


class SimpleChatAgent(AgentBase):
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
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        **model_kwargs,
    ):
        """Initialize agent with model and checkpoint configuration.

        Args:
            system_prompt: System message for the agent (default: helpful assistant)
            **model_kwargs: Parameters passed to ChatOpenAI (model, streaming, etc.)
        """
        super().__init__(**model_kwargs)
        self.system_prompt: str = system_prompt

    def _build_graph(self) -> CompiledStateGraph:
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
