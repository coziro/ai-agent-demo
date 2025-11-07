"""Base state classes for LangGraph agents."""

from typing import Annotated, ClassVar

from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel


class BasicMessagesState(BaseModel):
    """Basic state schema for agent conversation history.

    This class can be used directly for simple agents or extended
    with additional fields for more complex agents.

    Attributes:
        messages: List of conversation messages with automatic message reduction.
    """

    MESSAGES: ClassVar[str] = "messages"

    messages: Annotated[list[AnyMessage], add_messages]

    def get_last_message_content(self) -> str:
        """Get the content of the last message in the conversation.

        Returns:
            String content of the last message.
        """
        return str(self.messages[-1].content)
