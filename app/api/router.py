from fastapi import APIRouter
from app.api.routes import users, schemes, chats, messages

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(schemes.router, prefix="/schemes", tags=["schemes"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])