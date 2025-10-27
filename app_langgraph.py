import chainlit as cl
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph

model = ChatOpenAI(model="gpt-5-nano")

def call_llm(state: MessagesState):
    message = state["messages"]
    response = model.invoke(message)
    return {"messages": [response]}

graph = StateGraph(MessagesState)
graph.add_node(call_llm)
graph.add_edge(START, "call_llm")
graph.add_edge("call_llm", END)
agent = graph.compile()

@cl.on_message
async def on_message(msg: cl.Message):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": msg.content}]}
    )
    print(response)
    last_message = response["messages"][-1].content
    await cl.Message(content=last_message).send()
