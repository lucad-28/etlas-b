from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, UUID4

class SchemeBase(BaseModel):
    __tablename__ : str = "scheme"
    id: UUID4
    title: str
    content: str
    attachment_url: str | None
    created_at: datetime

class SchemeDB(SchemeBase):
    user_id: UUID4

class SchemeCreate(SchemeBase):
    user_id: UUID4
    attachment_url: str | None
    id: None = None
    created_at: None = None

    ordered_params: list  = ["title", "content", "user_id", "attachment_url"]

class SchemeUpdate(SchemeBase):
    title: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)
    attachment_url: Optional[str] = Field(default=None)

    created_at: None = None
    
    ordered_params: list  = ["id", "title", "content", "attachment_url"]

class MultiScheme(BaseModel):
    """Modelo para la paginación de esquemas"""
    total: int
    limit: int
    offset: int
    pages: int 
    data: List[SchemeBase]

class DeleteScheme(BaseModel):
    id: UUID4