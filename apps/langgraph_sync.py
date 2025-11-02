from typing import ClassVar

import chainlit as cl
from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

SYSTEM_PROMPT = "You are a helpful assistant."

model = ChatOpenAI(model="gpt-5-nano")

CHAT_HISTORY_KEY = "chat_history_key"


def load_chat_history() -> list[AnyMessage]:
    """Load the chat history from the user session, seeding with the system prompt if absent.

    Returns:
        list[AnyMessage]: The conversation history stored in the Chainlit user session.
    """
    chat_history = cl.user_session.get(CHAT_HISTORY_KEY)
    if chat_history is None:
        chat_history = [SystemMessage(SYSTEM_PROMPT)]
        cl.user_session.set(CHAT_HISTORY_KEY, chat_history)
    return chat_history


class ChatState(BaseModel):
    """State schema for the chat agent graph.

    This class defines the structure of the state that flows through the
    LangGraph nodes. It uses Pydantic BaseModel for runtime validation
    and type safety.

    Class Variables:
        MESSAGES: Field name constant for the messages field. Used to ensure
            consistency when accessing or updating the state.

    Attributes:
        messages: List of conversation messages including system prompts,
            user inputs, and AI responses.
    """

    # Field name
    MESSAGES: ClassVar[str] = "messages"

    # State Field
    messages: list[AnyMessage]


async def call_llm(state: ChatState) -> dict:
    """Call the LLM with the current conversation history.

    This node function invokes the language model with the complete message
    history from the chat state and returns a partial state update containing
    the AI's response.

    Args:
        state: Current chat state containing the message history.

    Returns:
        A dictionary containing the partial state update with the AI's response.
        The dictionary uses ChatState.MESSAGES as the key.
    """
    chat_history = state.messages
    response = await model.ainvoke(chat_history)
    update_field = {ChatState.MESSAGES: [response]}
    return update_field


graph = StateGraph(ChatState)
graph.add_node(call_llm)
graph.add_edge(START, call_llm.__name__)
graph.add_edge(call_llm.__name__, END)
agent = graph.compile()


@cl.on_chat_start
async def on_chat_start() -> None:
    load_chat_history()


@cl.on_message
async def on_message(user_request: cl.Message) -> None:
    try:
        chat_history = load_chat_history()
        chat_history.append(HumanMessage(user_request.content))

        current_state = ChatState(messages=chat_history)
        updated_state = await agent.ainvoke(current_state)
        updated_state = ChatState(**updated_state)
        last_message: AIMessage = updated_state.messages[-1]
        chat_history.append(last_message)

        user_response = cl.Message(content=last_message.content)
        await user_response.send()

    except Exception as e:
        await cl.ErrorMessage(content=repr(e)).send()
        raise e

