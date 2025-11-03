import chainlit as cl

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
        input_state = SimpleChatState(
            user_request=user_request.content
        )
        response_dict = await agent.graph.ainvoke(
            input=input_state,
            config=agent.config,
        )
        updated_state = SimpleChatState(**response_dict)
        last_message_content = updated_state.get_last_message_content()
        user_response = cl.Message(content=last_message_content)
        await user_response.send()

    except Exception as e:
        await cl.ErrorMessage(content=repr(e)).send()
        raise e
