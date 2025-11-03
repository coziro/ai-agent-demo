from langchain_openai import ChatOpenAI

from ..state import ChatState


async def call_llm(state: ChatState) -> dict:
    """Call the LLM with the current conversation history.

    This node function invokes the language model with the complete message
    history from the chat state and returns a partial state update containing
    the AI's response.

    Args:
        state: Current chat state containing the message history.

    Returns:
        A dictionary containing the partial state update with the AI's response.
        The dictionary uses ChatState.MESSAGES as the key.
    """
    model = ChatOpenAI(model="gpt-5-nano", streaming=True)
    chat_history = state.messages
    response = await model.ainvoke(chat_history)
    update_field = {ChatState.MESSAGES: [response]}
    return update_field
