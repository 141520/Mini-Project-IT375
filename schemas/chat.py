from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ChatRequest(BaseModel):
    game_id: int
    question: str
    conversation_id: Optional[int] = None


class Citation(BaseModel):
    page: int
    snippet: str


class ChatResponse(BaseModel):
    conversation_id: int
    message_id: Optional[int] = None
    answer: str
    citations: List[Citation] = []


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    citations: Optional[str] = None
    rating: int
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: int
    game_id: int
    title: str
    is_pinned: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class RateRequest(BaseModel):
    rating: int  # -1, 0, 1
