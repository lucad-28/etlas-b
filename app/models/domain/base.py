from typing import Any

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str
    
    # Genera automáticamente el nombre de la tabla
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Columnas comunes para todos los modelos
    id = Column(Integer, primary_key=True, index=True)