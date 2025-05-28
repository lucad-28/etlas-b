from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Union

from app.api.dependencies import get_db
from app.models.schemas.chat import MultiChat, ChatBase, ChatCreate, ChatUpdate
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

@router.get("/", response_model=MultiChat)
def read_chats(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    chats = chat_service.get_multi(db, limit=limit, skip=skip)
    return chats

@router.post("/by", response_model=Union[ChatBase, MultiChat])
async def read_chat(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    
    chat_id = data.get("id")
    if chat_id:
        chat = chat_service.get(db, id=chat_id)
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
        return chat
    
    user_id = data.get("user_id")
    if user_id:
        chats = chat_service.get_by_user_id(db, user_id=user_id)
        if not chats:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chats not found")
        return chats
    
    scheme_id = data.get("scheme_id")
    if scheme_id:
        chats = chat_service.get_by_scheme_id(db, scheme_id=scheme_id)
        if not chats:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chats not found")
        return chats
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide 'id', 'user_id' or 'scheme_id'")

@router.post("/", response_model=ChatBase)
async def create_chat(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    name_chat = data.get("name_chat")
    user_id = data.get("user_id")
    scheme_id = data.get("scheme_id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID is required")

    obj_in = ChatCreate(name_chat=name_chat, 
                        user_id=user_id,
                        scheme_id=scheme_id)

    chat = chat_service.create(db, obj_in=obj_in)
    return chat

@router.put("/", response_model=ChatBase)
async def update_chat(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    chat_id = data.get("id")
    name_chat = data.get("name_chat")

    if not chat_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chat ID is required")
    if not name_chat:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required")
    
    obj_in = ChatUpdate(id=chat_id, name_chat=name_chat)
    
    chat = chat_service.update(db, obj_in=obj_in)
    return chat

@router.delete("/", response_model=ChatBase)
async def delete_chat(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    chat_id = data.get("id")

    if not chat_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chat ID is required")
    
    obj_in = ChatBase(id=chat_id)
    
    chat = chat_service.remove(db, id=chat_id, obj_in=obj_in)
    return chat

