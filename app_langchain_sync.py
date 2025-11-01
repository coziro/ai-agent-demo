import chainlit as cl
from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

SYSTEM_PROMPT = "You are a helpful assistant."

model = ChatOpenAI(model="gpt-5-nano")

CHAT_HISTORY_KEY = "session_chat_history"


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


@cl.on_chat_start
async def on_chat_start() -> None:
    load_chat_history()


@cl.on_message
async def on_message(request_message: cl.Message) -> None:
    try:
        chat_history = load_chat_history()
        chat_history.append(HumanMessage(request_message.content))

        model_response = await model.ainvoke(chat_history)
        chat_history.append(AIMessage(model_response.content))

        reply_message = cl.Message(content=model_response.content)
        await reply_message.send()

    except Exception as e:
        await cl.ErrorMessage(content=repr(e)).send()
