"""Simple chat agent implementation with LangGraph checkpoint mechanism.

This package provides a simple chat agent that uses LangGraph's checkpoint mechanism
for conversation history persistence, decoupling state management from UI frameworks.

Key features:
- Agent class pattern with dependency injection
- Checkpoint-based conversation history (InMemorySaver)
- Pydantic BaseModel for type-safe state management
- UI framework independent (works with Chainlit, Streamlit, CLI, etc.)

Classes:
    SimpleChatAgent: LangGraph agent with checkpoint mechanism
    SimpleChatState: Pydantic model for agent state

Example:
    >>> from ai_agent_demo.simple_chat import SimpleChatAgent, SimpleChatState
    >>> agent = SimpleChatAgent()
    >>> input_state = SimpleChatState(user_request="Hello")
    >>> result = await agent.graph.ainvoke(input_state, config=agent.config)
"""

from .agent import SimpleChatAgent
from .state import SimpleChatState

__all__ = [
    "SimpleChatAgent",
    "SimpleChatState",
]
