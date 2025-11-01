from typing import TypedDict

import chainlit as cl
from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

SYSTEM_PROMPT = "You are a helpful assistant."

model = ChatOpenAI(model="gpt-5-nano")

CHAT_HISTORY_KEY = "chat_history_key"


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


class ChatState(TypedDict):
    messages: list[AnyMessage]


async def call_llm(state: ChatState) -> ChatState:
    chat_history = state["messages"]
    response = await model.ainvoke(chat_history)
    return {"messages": [response]}


graph = StateGraph(ChatState)
graph.add_node(call_llm)
graph.add_edge(START, "call_llm")
graph.add_edge("call_llm", END)
agent = graph.compile()


@cl.on_chat_start
async def on_chat_start() -> None:
    load_chat_history()


@cl.on_message
async def on_message(request_message: cl.Message) -> None:
    try:
        chat_history = load_chat_history()
        chat_history.append(HumanMessage(request_message.content))

        agent_response = await agent.ainvoke({"messages": chat_history})
        last_message: AIMessage = agent_response["messages"][-1]
        chat_history.append(last_message)

        reply_message = cl.Message(content=last_message.content)
        await reply_message.send()

    except Exception as e:
        await cl.ErrorMessage(content=repr(e)).send()

