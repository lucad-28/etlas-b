from app.models.domain.base import Base
from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, UUID, Text, func
from sqlalchemy.orm import relationship

class Message(Base):
    """Modelo para mensajes en la base de datos"""
    id = Column(Integer, primary_key=True, index=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    contentAnalysis = Column(Text, nullable=False)
    contentComment = Column(Text, nullable=False)
    contentCode = Column(Text, nullable=False)
    contentExecutableCode = Column(Text, nullable=True, default=None)

    # Relación con la tabla de chats
    chatId = Column(Integer, ForeignKey("chat.id"),  nullable=False)

    attachment = relationship("Attachment", back_populates="messageId")