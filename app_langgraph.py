import chainlit as cl
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph

model = ChatOpenAI(model="gpt-5-nano")

async def call_llm(state: MessagesState):
    message = state["messages"]
    response = await model.ainvoke(message)
    return {"messages": [response]}

graph = StateGraph(MessagesState)
graph.add_node(call_llm)
graph.add_edge(START, "call_llm")
graph.add_edge("call_llm", END)
agent = graph.compile()


@cl.on_chat_start
async def on_chat_start():
    system_msg = SystemMessage("You are a helpful assistant.")
    messages = [system_msg]
    cl.user_session.set("messages", messages)


@cl.on_message
async def on_message(msg: cl.Message):
    messages = cl.user_session.get("messages")

    human_msg = HumanMessage(msg.content)
    messages.append(human_msg)

    response = await agent.ainvoke({"messages": messages})

    last_message = response["messages"][-1].content
    ai_msg = AIMessage(last_message)
    messages.append(ai_msg)
    await cl.Message(content=last_message).send()
