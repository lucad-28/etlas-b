from app.models.domain.base import Base
from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, UUID, func
from sqlalchemy.orm import relationship

class Attachment(Base):
    """Modelo para archivos adjuntos en la base de datos"""
    id = Column(UUID, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    messageId = Column(UUID, ForeignKey("message.id"),  nullable=False)