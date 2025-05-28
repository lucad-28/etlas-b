from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.schemas.chat import ChatCreate, ChatUpdate, MultiChat, ChatBase, DeleteChat
from app.repositories.base import BaseRepository

class ChatRepository(BaseRepository[ChatBase, ChatCreate, ChatUpdate, MultiChat, DeleteChat]):
    """
    Repositorio para operaciones específicas de chats
    """    
    def get_by_user_id(self, db: Session, *, user_id: str) -> MultiChat:
        """
        Obtiene chats por el ID de usuario
        """
        result = db.execute(
            text(f"SELECT * FROM get_all_{self.__tablename__}s_by_user_id(:user_id)"),
            {"user_id": user_id}
        )
        records = result.scalar()
        if not records:
            return None
        return self.multi_validator(records)
    
    def get_by_scheme_id(self, db: Session, *, scheme_id: str) -> MultiChat:
        """
        Obtiene chats por el ID de esquema
        """
        result = db.execute(
            text(f"SELECT * FROM get_{self.__tablename__}_by_scheme_id(:scheme_id)"),
            {"scheme_id": scheme_id}
        )
        records = result.scalar()
        if not records:
            return None
        return self.multi_validator(records)
    
    def get_all_chats_by_user_id(self, db: Session, *, user_id: str, skip: int = 0, limit: int = 10) -> MultiChat:
        """
        Obtiene todos los chats por el ID de usuario
        """
        result = db.execute(
            text(f"SELECT * FROM get_all_{self.__tablename__}s_by_user_id(:user_id, :limit, :skip)"),
            {"user_id": user_id, "limit": limit, "skip": skip}
        )
        records = result.scalar()
        if not records:
            return None
        return self.multi_validator(records)
    
    def get_all_chats_by_scheme_id(self, db: Session, *, scheme_id: str, skip: int = 0, limit: int = 10) -> MultiChat:
        """
        Obtiene todos los chats por el ID de esquema
        """
        result = db.execute(
            text(f"SELECT * FROM get_all_{self.__tablename__}s_by_scheme_id(:scheme_id, :limit, :skip)"),
            {"scheme_id": scheme_id, "limit": limit, "skip": skip}
        )
        records = result.scalar()
        if not records:
            return None
        return self.multi_validator(records)
    
