import chainlit as cl

from ai_agent_demo.common import BasicMessagesState
from ai_agent_demo.email_draft import EmailDraftAgent

AGENT_KEY = "agent_key"


def load_agent() -> EmailDraftAgent:
    agent = cl.user_session.get(AGENT_KEY)
    if agent is None:
        agent = EmailDraftAgent()
        cl.user_session.set(AGENT_KEY, agent)
    return agent


@cl.on_chat_start
async def on_chat_start() -> None:
    load_agent()


@cl.on_message
async def on_message(user_query: cl.Message) -> None:
    try:
        agent = load_agent()
        state: BasicMessagesState = await agent.call(user_query.content)
        last_message_content: str = state.get_last_message_content()
        await cl.Message(last_message_content).send()

    except Exception as e:
        await cl.ErrorMessage(content=repr(e)).send()
        raise e
