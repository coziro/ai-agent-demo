import chainlit as cl
from langchain.messages import AIMessage

from ai_agent_demo.simple_chat import SimpleChatAgent, SimpleChatState

AGENT_KEY = "agent_key"


def load_agent() -> SimpleChatAgent:
    agent = cl.user_session.get(AGENT_KEY)
    if agent is None:
        agent = SimpleChatAgent()
        cl.user_session.set(AGENT_KEY, agent)
    return agent


@cl.on_chat_start
async def on_chat_start() -> None:
    load_agent()


@cl.on_message
async def on_message(user_request: cl.Message) -> None:
    try:
        agent = load_agent()
        input_state = SimpleChatState(user_request=user_request.content)

        reply_message = cl.Message(content="")
        async for message, _ in agent.graph.astream(
            input_state,
            config=agent.config,
            stream_mode="messages",
        ):
            if not isinstance(message, AIMessage):
                continue

            message_content = message.content
            if isinstance(message_content, str) and message_content:
                await reply_message.stream_token(message_content)

        await reply_message.send()

    except Exception as e:
        await cl.ErrorMessage(content=repr(e)).send()
        raise e
