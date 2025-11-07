import uuid
from abc import ABC, abstractmethod
from typing import Annotated, ClassVar

from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel

DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."


class AgentBase(ABC):
    def __init__(
        self,
        model_name: str = "gpt-5-nano",
        streaming: bool = True,
    ):
        # create model
        self.model = ChatOpenAI(
            model=model_name,
            streaming=streaming,
        )

        # create config
        self.config = RunnableConfig(configurable={"thread_id": str(uuid.uuid4)})

        # build graph
        self.graph: CompiledStateGraph = self._build_graph()

    @abstractmethod
    def _build_graph(self) -> CompiledStateGraph: ...


class AgentState(BaseModel):
    MESSAGES: ClassVar[str] = "messages"

    messages: Annotated[list[AnyMessage], add_messages]

    def get_last_message_content(self) -> str:
        return str(self.messages[-1].content)


class EmailDraftAgent(AgentBase):
    def __init__(
        self,
        model_name: str = "gpt-5-nano",
        streaming: bool = True,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ):
        super().__init__(model_name=model_name, streaming=streaming)
        self.first_call: bool = True
        self.system_prompt = system_prompt

    def _build_graph(self) -> CompiledStateGraph:
        graph = StateGraph(AgentState)
        graph.add_node(self.receive_input)
        graph.add_edge(START, self.receive_input.__name__)
        graph.add_edge(self.receive_input.__name__, END)

        checkpointer = InMemorySaver()
        return graph.compile(checkpointer=checkpointer)

    async def receive_input(self, state: AgentState) -> dict:
        response: AIMessage = await self.model.ainvoke(state.messages)
        return {AgentState.MESSAGES: [response]}

    async def call(self, user_query: str):
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
- [ ] モデルパラメータをまとめる。 model_paramsにして一気に渡す
- [ ] 共通クラスは別ファイルに分ける
"""
