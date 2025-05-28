from sqlalchemy import Boolean, Column, String, Integer, UUID
from sqlalchemy.orm import relationship

from app.models.domain.base import Base


class User(Base):
    """Modelo para usuarios en la base de datos"""
    id= Column(UUID, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    email_verified = Column(Boolean, nullable=True, default=None)
    image = Column(String(255), nullable=True, default=None)
        
    # Relación con la tabla de usuarios
    users = relationship("Scheme", back_populates="userId")