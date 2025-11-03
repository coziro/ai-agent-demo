from typing import cast

import chainlit as cl
from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage

from ai_agent_demo.simple_chat import ChatState, create_agent

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
        response_dict = await agent.ainvoke(current_state)
        updated_state = ChatState(**response_dict)
        last_message = updated_state.messages[-1]
        assert isinstance(last_message, AIMessage)
        chat_history.append(last_message)

        user_response = cl.Message(content=str(last_message.content))
        await user_response.send()

    except Exception as e:
        await cl.ErrorMessage(content=repr(e)).send()
        raise e
