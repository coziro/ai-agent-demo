"""Simple chat agent module.

This module provides a basic conversational AI agent implementation using LangGraph.
The agent maintains conversation history and responds to user messages using an LLM.

Exports:
    ChatState: State schema for the chat agent
    call_llm: Node function that invokes the LLM
    create_agent: Factory function to create and compile the agent graph
"""

from .agent import create_agent
from .node import call_llm
from .state import ChatState

__all__ = [
    "ChatState",
    "call_llm",
    "create_agent",
]
