from sqlalchemy.orm import Session
from app.models.schemas.chat import MultiChat, ChatBase, ChatUpdate, DeleteChat
from app.repositories.chat_repository import ChatRepository

class ChatService:
    def __init__(self):
        self.repository = ChatRepository()
    
    def create(self, db: Session, *, obj_in: ChatBase) -> ChatBase:
        return self.repository.create(db, obj_in=obj_in)

    def update(self, db: Session, *, obj_in: ChatUpdate) -> ChatBase:
        db_obj = self.repository.get(db, id=obj_in.id)
        if not db_obj:
            raise Exception("Chat not found")
        
        return self.repository.update(db, db_obj=db_obj, obj_in=obj_in)
    
    def remove(self, db: Session, *, id: int) -> DeleteChat:
        return self.repository.remove(db, id=id)

    def get(self, db: Session, *, id: int) -> ChatBase:
        return self.repository.get(db, id=id)

    def get_multi(self, db: Session, *, limit: int = 100, skip: int = 0) -> MultiChat:
        return self.repository.get_multi(db, limit=limit, skip=skip)

    def get_by_user_id(self, db: Session, *, user_id: str) -> MultiChat:
        return self.repository.get_by_user_id(db, user_id=user_id)
    
    def get_by_scheme_id(self, db: Session, *, scheme_id: str) -> MultiChat:
        return self.repository.get_by_scheme_id(db, scheme_id=scheme_id)
    
    def get_all_chats_by_user_id(self, db: Session, *, user_id: str, skip: int = 0, limit: int = 10) -> MultiChat:
        return self.repository.get_all_chats_by_user_id(db, user_id=user_id, skip=skip, limit=limit)
    
    def get_all_chats_by_scheme_id(self, db: Session, *, scheme_id: str, skip: int = 0, limit: int = 10) -> MultiChat:
        return self.repository.get_all_chats_by_scheme_id(db, scheme_id=scheme_id, skip=skip, limit=limit)