from pydantic import BaseModel
from typing import Optional, Literal, Any


class MemoryCreate(BaseModel):
    title: str
    description: Optional[str] = None


class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class RecordCreate(BaseModel):
    content: str
    metadata: Optional[Any] = None


class ChatSend(BaseModel):
    memory_id: str
    message: str


class ChatMessageOut(BaseModel):
    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: str
