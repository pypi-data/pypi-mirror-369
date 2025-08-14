from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Conversation(BaseModel):
    """
    Represents a single conversation.
    """

    id: str = Field(..., description="The ID of the conversation.")
    name: str = Field(..., description="The name of the conversation.")
    inputs: Dict[str, Any] = Field(
        ..., description="The inputs of the conversation."
    )
    status: str = Field(..., description="The status of the conversation.")
    introduction: str = Field(
        ..., description="The introduction of the conversation."
    )
    created_at: int = Field(
        ..., description="The creation time of the conversation."
    )
    updated_at: int = Field(
        ..., description="The last update time of the conversation."
    )


class ConversationsResponse(BaseModel):
    """
    Represents the response for a list of conversations.
    """

    data: List[Conversation] = Field(
        ..., description="The list of conversations."
    )
    has_more: bool = Field(
        ..., description="Whether there are more conversations."
    )
    limit: int = Field(..., description="The limit of the conversations.")


class ConversationRequest(BaseModel):
    """
    Represents the request for a list of conversations.
    """

    user: str = Field(..., description="The user of the conversation.")
    last_message_id: Optional[str] = Field(
        default=None, description="The last message ID of the conversation."
    )
    limit: int = Field(
        default=20, description="The limit of the conversations."
    )
    sort_by: str = Field(
        default="-updated_at", description="The sort by of the conversations."
    )
