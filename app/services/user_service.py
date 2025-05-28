from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.schemas.user import MultiUser, UserBase
from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self):
        self.repository = UserRepository()
    
    def get(self, db: Session, *, id: int) -> UserBase:
        return self.repository.get(db, id=id)

    def get_by_email(self, db: Session, *, email: str) -> UserBase:
        return self.repository.get_by_email(db, email=email)
    
    def get_multi(self, db: Session, *, limit = 100, skip = 0) -> MultiUser:
        return self.repository.get_multi(db, limit=limit, skip=skip)