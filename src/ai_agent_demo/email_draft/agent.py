from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel

from ai_agent_demo.common import AgentBase, BasicMessagesState

DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant. Create email draft based on your's input."


class EmailDraft(BaseModel):
    """Email draft containing subject and body.

    Attributes:
        subject: Email subject line
        body: Email body content
    """

    subject: str
    body: str


class AgentState(BasicMessagesState):
    """Agent state with optional email draft.

    Attributes:
        messages: Conversation message history
        email_draft: Optional email draft being composed
    """

    email_draft: EmailDraft | None = None


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
        self.tools = [self.draft_email]

        self.model_with_structure = self.model.with_structured_output(EmailDraft)

    def _build_graph(self) -> CompiledStateGraph:
        """Build a simple single-node graph with memory checkpoint."""
        graph = StateGraph(AgentState)
        graph.add_node(self.receive_input)
        # TODO: tool情報の持ち方を考える
        graph.add_node("tools", ToolNode([self.draft_email]))

        graph.add_edge(START, self.receive_input.__name__)
        graph.add_conditional_edges(self.receive_input.__name__, tools_condition)
        graph.add_edge("tools", self.receive_input.__name__)

        checkpointer = InMemorySaver()
        return graph.compile(checkpointer=checkpointer)

    async def receive_input(self, state: BasicMessagesState) -> dict:
        """Process user input and generate AI response.

        Args:
            state: Current agent state containing message history.

        Returns:
            Dictionary with new AI message to add to state.
        """
        model_with_tool = self.model.bind_tools(self.tools)
        response: AIMessage = await model_with_tool.ainvoke(state.messages)
        return {BasicMessagesState.MESSAGES: [response]}

    def draft_email(self, users_input: str) -> EmailDraft:
        """Based on the user's input, create draft email (subject and body)

        Args:
            users_input: user's input
        """
        prompt = "Based on user's input, create an email draft"
        messages = [SystemMessage(prompt), HumanMessage(users_input)]
        model_with_structure = self.model.with_structured_output(EmailDraft)
        response = model_with_structure.invoke(messages)
        assert isinstance(response, EmailDraft)

        print("=== DEBUG (draft email) ===")
        print(type(response))
        print(response)
        return response

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

        input_state = {AgentState.MESSAGES: messages}
        response_dict = await self.graph.ainvoke(
            input=input_state,
            config=self.config,
        )
        print("=== DEBUG ===")
        print(response_dict)
        updated_state = AgentState(**response_dict)
        return updated_state


"""
TODO
- [ ] リファクタリング
- [ ] ロギング
- [ ] プロンプト改善
- [ ] 表示内容の分離
    - [ ] メールドラフト
    - [ ] AIのコメント
"""
