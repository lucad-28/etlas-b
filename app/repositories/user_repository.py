from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.schemas.user import UserCreate, UserUpdate, MultiUser, UserBase, UserDelete
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserBase, UserCreate, UserUpdate, MultiUser, UserDelete]):
    """
    Repositorio para operaciones específicas de usuarios
    """    
    def get_by_email(self, db: Session, *, email: str) -> UserBase:
        """
        Obtiene un usuario por su correo electrónico
        """
        result = db.execute(
            text(f"SELECT * FROM get_{self.__tablename__}_by_email(:email)"),
            {"email": email}
        )
        db.commit()

        record = result.scalar()
        if not record:
            return None
        return self.base_validator(record)


    def create(self, db, *, obj_in):
        pass

    def update(self, db: Session, *, db_obj: UserBase, obj_in: Union[UserUpdate, Dict[str, Any]]) -> UserBase:
        pass

    def remove(self, db: Session, *, id: str) -> UserBase:
        pass
    