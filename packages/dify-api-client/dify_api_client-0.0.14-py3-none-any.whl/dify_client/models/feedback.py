from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Rating(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class FeedbackRequest(BaseModel):
    rating: Optional[Rating] = None
    user: str


class FeedbackResponse(BaseModel):
    result: str  # success
