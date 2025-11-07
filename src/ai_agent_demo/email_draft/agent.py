from typing import Annotated, ClassVar

from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel

from ai_agent_demo.common import AgentBase

DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."


class AgentState(BaseModel):
    """State schema for agent conversation history.

    Attributes:
        messages: List of conversation messages with automatic message reduction.
    """

    MESSAGES: ClassVar[str] = "messages"

    messages: Annotated[list[AnyMessage], add_messages]

    def get_last_message_content(self) -> str:
        """Get the content of the last message in the conversation.

        Returns:
            String content of the last message.
        """
        return str(self.messages[-1].content)


class EmailDraftAgent(AgentBase):
    """Agent for drafting emails with conversation memory.

    Args:
        system_prompt: Initial system prompt for the agent.
        **model_kwargs: Parameters passed to ChatOpenAI.
    """

    def __init__(
        self,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        **model_kwargs,
    ):
        super().__init__(**model_kwargs)

        self.first_call: bool = True
        self.system_prompt = system_prompt

    def _build_graph(self) -> CompiledStateGraph:
        """Build a simple single-node graph with memory checkpoint."""
        graph = StateGraph(AgentState)
        graph.add_node(self.receive_input)
        graph.add_edge(START, self.receive_input.__name__)
        graph.add_edge(self.receive_input.__name__, END)

        checkpointer = InMemorySaver()
        return graph.compile(checkpointer=checkpointer)

    async def receive_input(self, state: AgentState) -> dict:
        """Process user input and generate AI response.

        Args:
            state: Current agent state containing message history.

        Returns:
            Dictionary with new AI message to add to state.
        """
        response: AIMessage = await self.model.ainvoke(state.messages)
        return {AgentState.MESSAGES: [response]}

    async def call(self, user_query: str):
        """Handle user query and return updated state.

        Args:
            user_query: User's input message.

        Returns:
            Updated AgentState with conversation history.
        """
        messages = []
        if self.first_call:
            messages.append(SystemMessage(self.system_prompt))
            self.first_call = False
        messages.append(HumanMessage(user_query))

        input_state = {AgentState.MESSAGES: messages}
        response_dict = await self.graph.ainvoke(
            input=input_state,
            config=self.config,
        )
        print("=== DEBUG ===")
        print(response_dict)
        updated_state = AgentState(**response_dict)
        return updated_state
