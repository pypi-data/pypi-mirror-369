from typing import List, Optional

from pydantic import BaseModel

from .base import CompletionInputs, File, Metadata, Mode, ResponseMode


class CompletionRequest(BaseModel):
    inputs: CompletionInputs
    response_mode: ResponseMode
    user: str
    conversation_id: Optional[str] = ""
    files: List[File] = []


class CompletionResponse(BaseModel):
    message_id: str
    conversation_id: Optional[str] = ""
    mode: Mode = Mode.COMPLETION
    answer: str
    metadata: Optional[Metadata] = None
    created_at: int  # unix timestamp seconds
