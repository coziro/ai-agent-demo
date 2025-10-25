import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage

model = ChatOpenAI(model="gpt-5-nano")
system_msg = SystemMessage("You are a helpful assistant.")

@cl.on_message
async def main(message: cl.Message):
    human_msg = HumanMessage(message.content)
    response = await model.ainvoke([system_msg, human_msg])
    await cl.Message(content=response.content).send()
