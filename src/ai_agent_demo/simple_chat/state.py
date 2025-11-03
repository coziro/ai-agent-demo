from typing import ClassVar

from langchain.messages import AnyMessage
from pydantic import BaseModel


class ChatState(BaseModel):
    """State schema for the chat agent graph.

    This class defines the structure of the state that flows through the
    LangGraph nodes. It uses Pydantic BaseModel for runtime validation
    and type safety.

    Class Variables:
        MESSAGES: Field name constant for the messages field. Used to ensure
            consistency when accessing or updating the state.

    Attributes:
        messages: List of conversation messages including system prompts,
            user inputs, and AI responses.
    """

    # Field name
    MESSAGES: ClassVar[str] = "messages"

    # State Field
    messages: list[AnyMessage]
