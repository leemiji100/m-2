from datetime import date as date_type
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------- 그림 공부 기록 (data) ----------

class DrawingRecordIn(BaseModel):
    date: date_type
    value: int = Field(..., ge=0, description="그날 그린 그림 개수")
    memo: Optional[str] = ""


class DrawingRecordUpdate(BaseModel):
    date: Optional[date_type] = None
    value: Optional[int] = Field(None, ge=0)
    memo: Optional[str] = None


class DrawingRecordOut(BaseModel):
    id: str
    date: str
    value: int
    memo: Optional[str] = ""


class SummaryMetrics(BaseModel):
    total: float
    average: float
    max: float
    min: float


class SummaryOut(BaseModel):
    period: str
    count: int
    metrics: SummaryMetrics
    trend: str


# ---------- 대화 기록 (conversations) ----------

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ConversationCreate(BaseModel):
    title: str = "새 대화"
    messages: List[ChatMessage] = []


class ConversationOut(BaseModel):
    id: str
    created_at: str
    title: str


class ConversationDetailOut(ConversationOut):
    messages: List[ChatMessage]


# ---------- 채팅 (chat) ----------

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
