from typing import ClassVar, cast

import chainlit as cl
from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

# ==========================================
# Old simple_chat implementation (embedded)
# ==========================================


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
    model = ChatOpenAI(model="gpt-5-nano", streaming=True)
    chat_history = state.messages
    response = await model.ainvoke(chat_history)
    update_field = {ChatState.MESSAGES: [response]}
    return update_field


def create_agent():
    graph = StateGraph(ChatState)
    graph.add_node(call_llm)
    graph.add_edge(START, call_llm.__name__)
    graph.add_edge(call_llm.__name__, END)
    agent = graph.compile()
    return agent


# ==========================================
# Chainlit integration
# ==========================================

SYSTEM_PROMPT = "You are a helpful assistant."
CHAT_HISTORY_KEY = "chat_history_key"
agent = create_agent()


def load_chat_history() -> list[AnyMessage]:
    """Load the chat history from the user session, seeding with the system prompt if absent.

    Returns:
        list[AnyMessage]: The conversation history stored in the Chainlit user session.
    """
    chat_history = cl.user_session.get(CHAT_HISTORY_KEY)
    if chat_history is None:
        chat_history = [SystemMessage(SYSTEM_PROMPT)]
        cl.user_session.set(CHAT_HISTORY_KEY, chat_history)
    return cast(list[AnyMessage], chat_history)


@cl.on_chat_start
async def on_chat_start() -> None:
    load_chat_history()


@cl.on_message
async def on_message(user_request: cl.Message) -> None:
    try:
        chat_history = load_chat_history()
        chat_history.append(HumanMessage(user_request.content))

        current_state = ChatState(messages=chat_history)
        reply_message = cl.Message(content="")
        async for message, _ in agent.astream(
            current_state,
            stream_mode="messages",
        ):
            if not isinstance(message, AIMessage):
                continue

            message_content = message.content
            if isinstance(message_content, str) and message_content:
                await reply_message.stream_token(message_content)

        chat_history.append(AIMessage(reply_message.content))
        await reply_message.send()

    except Exception as e:
        await cl.ErrorMessage(content=repr(e)).send()
        raise e
