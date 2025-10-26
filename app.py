import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage, AIMessage

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
    
    msg = cl.Message(content="")
    full_response = ""
    async for chunk in model.astream(messages):
        if chunk.content:
            await msg.stream_token(chunk.content)
            full_response += chunk.content

    ai_msg = AIMessage(full_response)
    messages.append(ai_msg)
    await msg.send()

