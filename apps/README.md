# Apps - Implementation Patterns

This directory contains four different implementation patterns for building a chat application with LangChain and LangGraph.

## Overview

All implementations provide the same core functionality: a conversational AI chatbot with conversation history. The key differences lie in the framework used and how responses are delivered to the user.

## Implementation Matrix

|              | LangChain                  | LangGraph                 |
|--------------|----------------------------|---------------------------|
| **Sync**     | `langchain_sync.py`        | `langgraph_sync.py`       |
| **Streaming**| `langchain_streaming.py`   | `langgraph_streaming.py`  |

## Terminology

- **Sync**: Displays the complete response at once (uses `ainvoke()`)
- **Streaming**: Displays tokens progressively in real-time (uses `astream()`)

Note: Both versions use async/await for non-blocking I/O operations.

## Running the Apps

Each implementation can be run independently using Chainlit:

```bash
# LangChain with sync response
chainlit run apps/langchain_sync.py

# LangChain with streaming response
chainlit run apps/langchain_streaming.py

# LangGraph with sync response
chainlit run apps/langgraph_sync.py

# LangGraph with streaming response
chainlit run apps/langgraph_streaming.py
```

## Which One Should I Use?

- **For learning**: Start with `langchain_sync.py` (simplest)
- **For production**: Use `langchain_streaming.py` or `langgraph_streaming.py` (better UX)
- **For complex workflows**: Use LangGraph versions (supports multi-node graphs, conditional routing, etc.)

## Key Differences

### LangChain vs LangGraph

- **LangChain**: Simple, linear conversation flow
- **LangGraph**: Graph-based architecture, supports complex workflows with multiple nodes

### Sync vs Streaming

- **Sync**: Complete response appears at once
  - Pros: Simple implementation
  - Cons: User waits longer without feedback

- **Streaming**: Response appears token by token (like ChatGPT)
  - Pros: Better user experience, feels more responsive
  - Cons: Slightly more complex implementation

## Implementation Details

All implementations share:
- Conversation history management using Chainlit sessions
- Error handling for API failures
- System message support
- OpenAI GPT model integration

For more details, refer to the individual source files.
