"""State model for simple chat agent with checkpoint mechanism."""

from typing import ClassVar

from langchain.messages import AnyMessage
from pydantic import BaseModel


class SimpleChatState(BaseModel):
    """Pydantic model for chat conversation state.

    Attributes:
        USER_REQUEST: Field name constant
        CHAT_HISTORY: Field name constant
        user_request: Current user message content
        chat_history: Conversation history (None until initialized)
    """

    USER_REQUEST: ClassVar[str] = "user_request"
    CHAT_HISTORY: ClassVar[str] = "chat_history"

    user_request: str
    chat_history: list[AnyMessage] | None = None

    def get_last_message_content(self) -> str:
        """Get content of the last message in conversation history.

        Returns:
            Last message content as string, or empty string if no history
        """
        if self.chat_history:
            last_message: AnyMessage = self.chat_history[-1]
            return str(last_message.content)
        else:
            return ""
