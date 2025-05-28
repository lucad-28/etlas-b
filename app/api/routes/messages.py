from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Union

from app.api.dependencies import get_db
from app.models.schemas.message import MultiMessage, MessageBase, MessageCreate, MessageUpdate
from app.services.message_service import MessageService

router = APIRouter()
message_service = MessageService()

@router.get("/", response_model=MultiMessage)
def read_messages(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    messages = message_service.get_multi(db, limit=limit, skip=skip)
    return messages

@router.post("/by", response_model=Union[MessageBase, MultiMessage])
async def read_message(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    
    message_id = data.get("id")
    if message_id:
        message = message_service.get(db, id=message_id)
        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
        return message
    
    user_id = data.get("user_id")
    if user_id:
        messages = message_service.get_by_user_id(db, user_id=user_id)
        if not messages:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Messages not found")
        return messages
    
    chat_id = data.get("chat_id")
    if chat_id:
        messages = message_service.get_all_with_attachments_by_chat_id(db, chat_id=chat_id)
        if not messages:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Messages not found")
        return messages
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide 'id', 'user_id' or 'chat_id'")

@router.post("/", response_model=MessageBase)
async def send_message(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    role = data.get("role")
    content = data.get("content")
    chat_id = data.get("chat_id")
    attachments = data.get("attachments")

    # Use attachtment to upload files and use urls in create message
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role is required")
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content is required")
    if not chat_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chat ID is required")

    obj_in = MessageCreate(role=role, 
                           content=content,
                           chat_id=chat_id,
                           attachments=attachments)

    message = message_service.send_message(db, obj_in=obj_in)
    return message
