from typing import List, Optional, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field, UUID4
from .attachment import AttachmentCreate, AttachmentBase

class ContentAi(BaseModel):
    content_analysis: Optional[str] = Field(default=None)
    content_comment:  Optional[str] = Field(default=None)
    content_code:  Optional[str] = Field(default=None)
    content_executable_code:  Optional[str] = Field(default=None)

class ContentUser(BaseModel):
    content: Optional[str] = Field(default=None)

class MessageBase(BaseModel):
    __tablename__ : str = "message"
    id: UUID4
    created_at: datetime
    role: Literal["user", "ai"]
    content: Union[ContentUser, ContentAi]
    attachments: Optional[List[AttachmentBase]]

class MessageDB(MessageBase):
    chat_id: UUID4

class MessageCreate(MessageBase):
    chat_id: Optional[UUID4]
    id: None = None
    created_at: None = None
    attachments: Optional[List[AttachmentCreate]] = Field(default=None)

class MessageUpdate(BaseModel):
    pass

class MultiMessage(BaseModel):
    """Modelo para la paginación de mensajes"""
    total: int
    limit: int
    offset: int
    pages: int 
    data: List[MessageBase]

class DeleteMessage(BaseModel):
    id: UUID4

class MessageWithAttachment(MessageBase):
    attachments: List[AttachmentBase]


class UnitMessage(BaseModel):
    id: UUID4
    created_at: datetime
    role: Literal["user", "ai"]
    content: Union[ContentUser, ContentAi]

class ListMessage(BaseModel):
    data: List[UnitMessage]