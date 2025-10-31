import chainlit as cl
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph

model = ChatOpenAI(model="gpt-5-nano", streaming=True)


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
    try:
        messages = cl.user_session.get("messages")
        human_msg = HumanMessage(msg.content)
        messages.append(human_msg)

        msg = cl.Message(content="")
        full_response = ""
        async for message, _ in agent.astream({"messages": messages}, stream_mode="messages"):
            if message.content:
                await msg.stream_token(message.content)
                full_response += message.content

        ai_msg = AIMessage(full_response)
        messages.append(ai_msg)
        await msg.send()

    except Exception as e:
        error_msg = f"ERROR: {e}"
        await cl.ErrorMessage(content=error_msg).send()
