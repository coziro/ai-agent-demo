from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ai_agent_demo.common import AgentBase, BasicMessagesState

DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."


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
        graph = StateGraph(BasicMessagesState)
        graph.add_node(self.receive_input)
        graph.add_edge(START, self.receive_input.__name__)
        graph.add_edge(self.receive_input.__name__, END)

        checkpointer = InMemorySaver()
        return graph.compile(checkpointer=checkpointer)

    async def receive_input(self, state: BasicMessagesState) -> dict:
        """Process user input and generate AI response.

        Args:
            state: Current agent state containing message history.

        Returns:
            Dictionary with new AI message to add to state.
        """
        response: AIMessage = await self.model.ainvoke(state.messages)
        return {BasicMessagesState.MESSAGES: [response]}

    async def call(self, user_query: str):
        """Handle user query and return updated state.

        Args:
            user_query: User's input message.

        Returns:
            Updated BasicMessagesState with conversation history.
        """
        messages = []
        if self.first_call:
            messages.append(SystemMessage(self.system_prompt))
            self.first_call = False
        messages.append(HumanMessage(user_query))

        input_state = {BasicMessagesState.MESSAGES: messages}
        response_dict = await self.graph.ainvoke(
            input=input_state,
            config=self.config,
        )
        print("=== DEBUG ===")
        print(response_dict)
        updated_state = BasicMessagesState(**response_dict)
        return updated_state
