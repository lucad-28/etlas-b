from app.models.domain.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from sqlalchemy.sql import func

class Chat(Base):
    """Modelo para chats en la base de datos"""
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(255), nullable=False)
    attachmentUrl = Column(String(255), nullable=True, default=None)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    schemeId = Column(Integer, ForeignKey("scheme.id"),  nullable=False)
    userId = Column(Integer, ForeignKey("user.id"),  nullable=False)

