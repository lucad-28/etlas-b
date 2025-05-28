from typing import Optional, List
from pydantic import BaseModel, EmailStr, UUID4


# Propiedades compartidas
class UserBase(BaseModel):
    __tablename__ = "user"

    id: UUID4
    name: str
    email: EmailStr
    email_verified: Optional[bool] = None
    image: str

class MultiUser(BaseModel):
    """Modelo para la paginación de usuarios"""
    total: int
    limit: int
    offset: int
    pages: int 
    data: List[UserBase]

# Usuario completo devuelto por API
class UserResponse(UserBase):
    pass

class MultiUserResponse(MultiUser):
    pass

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserDelete(BaseModel):
    id: UUID4