import chainlit as cl
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-5-nano")


@cl.on_chat_start
async def on_chat_start():
    system_msg = SystemMessage("You are a helpful assistant.")
    messages = [system_msg]
    cl.user_session.set("messages", messages)


@cl.on_message
async def on_message(message: cl.Message):
    messages = cl.user_session.get("messages")

    human_msg = HumanMessage(message.content)
    messages.append(human_msg)

    response = await model.ainvoke(messages)
    ai_msg = AIMessage(response.content)
    messages.append(ai_msg)

    await cl.Message(content=response.content).send()
