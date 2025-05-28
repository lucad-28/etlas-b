from sqlalchemy.orm import Session
from app.models.schemas.scheme import MultiScheme, SchemeBase, SchemeUpdate, DeleteScheme
from app.repositories.scheme_repository import SchemeRepository

class SchemeService:
    def __init__(self):
        self.repository = SchemeRepository()
    
    def get(self, db: Session, *, id: int) -> SchemeBase:
        return self.repository.get(db, id=id)

    def get_by_user_id(self, db: Session, *, user_id: str) -> MultiScheme:
        return self.repository.get_by_user_id(db, user_id=user_id)
    
    def get_by_chat_id(self, db: Session, *, chat_id: str, limit: int = 10, skip: int = 0) -> MultiScheme:
        return self.repository.get_by_chat_id(db, chat_id=chat_id, limit=limit, skip=skip)
    
    def get_multi(self, db: Session, *, limit = 100, skip = 0) -> MultiScheme:
        return self.repository.get_multi(db, limit=limit, skip=skip)
    
    def create(self, db: Session, *, obj_in) -> SchemeBase:
        return self.repository.create(db, obj_in=obj_in)
    
    def update(self, db: Session, *, obj_in: SchemeUpdate) -> SchemeBase:
        db_obj = self.get(db, id=obj_in.id)
        if not db_obj:
            raise Exception("Scheme not found")
        
        # Update the fields of db_obj with the values from obj_in
        return self.repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def remove(self, db: Session, *, id: int) -> DeleteScheme:
        db_obj = self.get(db, id=id)
        if not db_obj:
            raise Exception("Scheme not found")
        
        return self.repository.remove(db, db_obj=db_obj)
