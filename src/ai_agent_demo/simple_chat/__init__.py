"""Simple chat agent implementation with LangGraph checkpoint mechanism.

This package provides a simple chat agent that uses LangGraph's checkpoint mechanism
for conversation history persistence, decoupling state management from UI frameworks.

Key features:
- Agent class pattern with dependency injection
- Checkpoint-based conversation history (InMemorySaver)
- Uses BasicMessagesState for type-safe state management
- UI framework independent (works with Chainlit, Streamlit, CLI, etc.)

Classes:
    SimpleChatAgent: LangGraph agent with checkpoint mechanism

Example:
    >>> from ai_agent_demo.simple_chat import SimpleChatAgent
    >>> agent = SimpleChatAgent()
    >>> result = await agent.call("Hello")
"""

from .agent import SimpleChatAgent

__all__ = [
    "SimpleChatAgent",
]
