from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Union
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.schemas.scheme import MultiScheme, SchemeBase, SchemeCreate, SchemeUpdate
from app.services.scheme_service import SchemeService

from fastapi import Request

router = APIRouter()
scheme_service = SchemeService()
@router.get("/", response_model=MultiScheme)
def read_schemes(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    schemes = scheme_service.get_multi(db, limit=limit, skip=skip)
    return schemes

@router.post("/by", response_model=Union[SchemeBase, MultiScheme])
async def read_scheme(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    
    scheme_id = data.get("id")
    if scheme_id:
        scheme = scheme_service.get(db, id=scheme_id)
        if not scheme:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found")
        return scheme
    
    user_id = data.get("user_id")
    if user_id:
        schemes = scheme_service.get_by_user_id(db, user_id=user_id)
        if not schemes:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schemes not found")
        return schemes
    
    chat_id = data.get("chat_id")
    if chat_id:
        schemes = scheme_service.get_by_chat_id(db, chat_id=chat_id)
        if not schemes:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schemes not found")
        return schemes

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide 'id' or 'name'")

@router.post("/", response_model=SchemeBase)
async def create_scheme(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    title = data.get("title")
    content = data.get("content")
    attachment_url = data.get("attachment_url")
    user_id = data.get("user_id")

    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required")
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content is required")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID is required")
    
    obj_in = SchemeCreate(title=title, 
                          content=content, 
                          user_id=user_id,
                          attachment_url=attachment_url)

    scheme = scheme_service.create(db, obj_in=obj_in)
    return scheme

@router.put("/", response_model=SchemeBase)
async def update_scheme(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    scheme_id = data.get("id")
    title = data.get("title")
    content = data.get("content")
    attachment_url = data.get("attachment_url")

    if not scheme_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scheme ID is required")
    
    obj_in = SchemeUpdate(id=scheme_id,
                           title=title, 
                          content=content, 
                          attachment_url=attachment_url)

    scheme = scheme_service.update(db, obj_in=obj_in)
    return scheme

@router.delete("/", response_model=SchemeBase)
async def delete_scheme(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    scheme_id = data.get("id")

    if not scheme_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scheme ID is required")
    
    scheme = scheme_service.remove(db, id=scheme_id)
    return scheme