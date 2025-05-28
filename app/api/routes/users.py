from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.schemas.user import MultiUserResponse, UserResponse
from app.services.user_service import UserService

from fastapi import Request

router = APIRouter()
user_service = UserService()

@router.get("/", response_model=MultiUserResponse)
def read_users(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    users = user_service.get_multi(db, limit=limit, skip=skip)
    return users

@router.post("/by", response_model=UserResponse)
async def read_user(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    email = data.get("email")

    if email:
        user = user_service.get_by_email(db, email=email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    
    user_id = data.get("id")
    if user_id:
        user = user_service.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide 'id' or 'email'")