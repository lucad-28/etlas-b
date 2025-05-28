from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, UUID4

class AttachmentBase(BaseModel):
    __tablename__ : str = "attachment"
    id: UUID4
    url: str
    created_at: datetime
    filename: str

class AttachmentDB(AttachmentBase):
    message_id: UUID4

class AttachmentCreate(AttachmentDB):
    message_id: UUID4
    id: None = None
    created_at: None = None

    ordered_params: list  = ["message_id", "url", "filename"]

class AttachmentUpdate(AttachmentBase):
    url: Optional[str] = Field(default=None)
    filename: Optional[str] = Field(default=None)
    created_at: None = None
    
    ordered_params: list  = ["id", "url", "filename"]

class MultiAttachment(BaseModel):
    """Modelo para la paginación de adjuntos"""
    total: int
    limit: int
    offset: int
    pages: int 
    data: List[AttachmentBase]

class DeleteAttachment(BaseModel):
    id: UUID4