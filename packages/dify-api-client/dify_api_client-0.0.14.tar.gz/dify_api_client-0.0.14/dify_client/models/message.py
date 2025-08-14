from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class HistoryMessage(BaseModel):
    """
    Represents a history message in a conversation.
    """

    id: str
    conversation_id: str
    inputs: Dict[str, Any]
    query: str
    answer: str
    message_files: List[str]
    feedback: Any = None  # Can be None or string
    retriever_resources: List[Any] = []  # Can be list of strings or dicts
    agent_thoughts: List[Any] = []  # Can be list of strings or dicts
    created_at: int = 0


class ConversationHistoryMessageRequest(BaseModel):
    conversation_id: str
    user: str
    first_id: Optional[str] = None
    limit: int = 20


class ConversationHistoryMessageResponse(BaseModel):
    data: List[HistoryMessage]
    has_more: bool
    limit: int
