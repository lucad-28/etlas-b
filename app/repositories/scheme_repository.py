from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.schemas.scheme import SchemeCreate, SchemeUpdate, MultiScheme, SchemeBase, DeleteScheme
from app.repositories.base import BaseRepository

class SchemeRepository(BaseRepository[SchemeBase, SchemeCreate, SchemeUpdate, MultiScheme, DeleteScheme]):
    """
    Repositorio para operaciones específicas de esquemas
    """    
    def get_by_user_id(self, db: Session, *, user_id: str) -> MultiScheme:
        """
        Obtiene esquemas por el ID de usuario
        """
        result = db.execute(
            text(f"SELECT * FROM get_all_{self.__tablename__}s_by_user_id(:user_id)"),
            {"user_id": user_id}
        )
        records = result.scalar()
        if not records:
            return None
        return self.multi_validator(records)
    
    def get_by_chat_id(self, db: Session, *, chat_id: str,  skip: int = 0, limit: int = 10) -> MultiScheme:
        """
        Obtiene esquemas por el ID de chat
        """
        result = db.execute(
            text(f"SELECT * FROM get_all_{self.__tablename__}s_by_chat_id(:chat_id, :limit, :skip)"),
            {"chat_id": chat_id, "limit": limit, "skip": skip}
        )
        records = result.scalar()
        if not records:
            return None
        return self.multi_validator(records)
    

    





