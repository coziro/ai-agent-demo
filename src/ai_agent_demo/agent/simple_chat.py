from langgraph.graph import END, START, StateGraph

from ai_agent_demo.node import call_llm
from ai_agent_demo.state import ChatState


def create_agent():
    graph = StateGraph(ChatState)
    graph.add_node(call_llm)
    graph.add_edge(START, call_llm.__name__)
    graph.add_edge(call_llm.__name__, END)
    agent = graph.compile()
    return agent
