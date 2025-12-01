from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.models.chat_history import MessageRole


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    session_id: str
    created_at: datetime
    tokens_used: Optional[int] = None  # 사용된 토큰 수
    model: Optional[str] = None  # 사용된 모델


class ChatHistoryResponse(BaseModel):
    id: int
    role: MessageRole
    content: str
    session_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
