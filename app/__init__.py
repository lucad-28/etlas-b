from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config.config import settings
from app.api.router import api_router

app = FastAPI(
    title="EtlAs",
    description="API automatizar procesos ETL con IA",
    version="1.0.0",
)

def create_app():
    app.add_middleware(CORSMiddleware, allow_origins=settings.ALLOWED_ORIGINS, allow_credentials=True, allow_methods=["POST", "PUT", "GET", "DELETE"], allow_headers=["*"])
    app.router.include_router(api_router, prefix="/v1", tags=["api"])
    return app
