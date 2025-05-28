from app.models.domain.base import Base
from sqlalchemy import Column, DateTime, String, Integer, UUID, ForeignKey, func
from sqlalchemy.orm import relationship

class Scheme(Base):
    """Modelo para esquemas en la base de datos"""
    id = Column(UUID, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(String(255), nullable=False)
    attachmentUrl = Column(String(255), nullable=True, default=None)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    userId = Column(UUID, ForeignKey("user.id"),  nullable=False)

    chats = relationship("Chat", back_populates="schemeId")
