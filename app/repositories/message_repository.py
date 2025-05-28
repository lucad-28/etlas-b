from typing import Any, List
from sqlalchemy.orm import Session
from sqlalchemy import Result, text

from app.models.schemas.message import MessageCreate, MessageUpdate, MultiMessage, MessageBase, DeleteMessage, ContentAi, ContentUser, ListMessage, UnitMessage
from app.repositories.base import BaseRepository

from fastapi.encoders import jsonable_encoder

class MessageRepository(BaseRepository[MessageBase, MessageCreate, MessageUpdate, MultiMessage, DeleteMessage]):
    """
    Repositorio para operaciones específicas de mensajes
    """    
    def get_multi(self, db, *, skip = 0, limit = 10):
        result = db.execute(
            text(f"SELECT * FROM get_all_{self.__tablename__}s_whit_content(:limit, :skip)"),
            {"limit": limit, "skip": skip} 
        )
        db.commit()

        records = result.scalar()
        return self.multi_validator(records)

    def create(self, db, *, obj_in):

        result: Result[Any] = None

        if isinstance(obj_in.content, ContentAi):
            result = db.execute(
                text(f"SELECT * FROM create_{self.__tablename__}(:chat_id, :role, :content, :content_analysis, :content_comment, :content_code, :content_executable_code)"),
                {
                    "chat_id": obj_in.chat_id,
                    "role": obj_in.role,
                    "content": None,
                    "content_analysis": obj_in.content.content_analysis,
                    "content_comment": obj_in.content.content_comment,
                    "content_code": obj_in.content.content_code,
                    "content_executable_code": obj_in.content.content_executable_code,
                }
            )
        elif isinstance(obj_in.content, ContentUser):
            result = db.execute(
                text(f"SELECT * FROM create_{self.__tablename__}(:chat_id, :role, :content)"),
                {
                    "chat_id": obj_in.chat_id,
                    "role": obj_in.role,
                    "content": obj_in.content.content,
                }
            )
        else:
            raise ValueError("Invalid content type")

        
        record = result.scalar()
        db.commit()
        if not record:
            return None
        
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["id"] = record["id"]
        obj_in_data["created_at"] = record["created_at"]

        return self.base_validator(obj_in_data)
    
    def get_by_user_id(self, db: Session, *, user_id: str) -> MultiMessage:
        """
        Obtiene mensajes por el ID de usuario
        """
        result = db.execute(
            text(f"SELECT * FROM get_all_{self.__tablename__}s_by_user_id(:user_id)"),
            {"user_id": user_id}
        )
        records = result.scalar()
        if not records:
            return None
        return self.multi_validator(records)
    
    def update(self):
        pass

    def get_all_with_attachments_by_chat_id(self, db: Session, *, chat_id: str,  skip: int = 0, limit: int = 10) -> MultiMessage:
        """
        Obtiene mensajes por el ID de chat
        """
        result = db.execute(
            text(f"SELECT * FROM get_all_{self.__tablename__}s_with_content_attachment_by_chatId(:chat_id, :limit, :skip)"),
            {"chat_id": chat_id, "limit": limit, "skip": skip}
        )
        records = result.scalar()
        if not records:
            return None
        return self.multi_validator(records)

    def get_full_messages_by_chat_id(self, db: Session, *, chat_id: str) -> ListMessage:
        """
        Obtiene mensajes por el ID de chat
        """
        result = db.execute(
            text(f"SELECT * FROM get_full_{self.__tablename__}s_with_content_by_chatId(:chat_id)"),
            {"chat_id": chat_id}
        )
        records = result.scalar()
        if not records:
            return None

        return ListMessage.model_validate(records)