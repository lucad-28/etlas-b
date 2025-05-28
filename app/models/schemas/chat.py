from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, UUID4

class ChatBase(BaseModel):
    __tablename__ : str = "chat"
    id: UUID4
    name_chat: Optional[str]
    created_at: datetime

class MultiChat(BaseModel):
    """Modelo para la paginación de chats"""
    total: int
    limit: int
    offset: int
    pages: int 
    data: List[ChatBase]

class ChatDB(ChatBase):
    user_id: UUID4
    scheme_id: UUID4

class MultiChatDB(MultiChat):
    data: List[ChatDB]

class ChatCreate(ChatBase):
    user_id: UUID4
    scheme_id: Optional[UUID4]
    id: None = None
    created_at: None = None

    ordered_params: list  = ["user_id", "scheme_id", "name_chat"]

class ChatUpdate(ChatBase):
    name_chat: str | None = Field(default=None)
    created_at: None = None
    
    ordered_params: list  = ["id", "user_id", "scheme_id", "name_chat"]

class DeleteChat(BaseModel):
    id: UUID4
