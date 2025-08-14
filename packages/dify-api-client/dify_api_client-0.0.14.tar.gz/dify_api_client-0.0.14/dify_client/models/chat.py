from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .base import File, ResponseMode
from .completion import CompletionResponse


class ChatRequest(BaseModel):
    query: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    response_mode: ResponseMode
    user: str
    conversation_id: Optional[str] = (
        ""  # pass the previous message's conversation_id to continue the conversation
    )
    files: List[File] = []
    auto_generate_name: bool = True


class ChatResponse(CompletionResponse):
    pass


class ChatSuggestRequest(BaseModel):
    user: str


class ChatSuggestResponse(BaseModel):
    result: str
    data: List[str] = []
