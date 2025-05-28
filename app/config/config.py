import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from app.utils.singleton import singleton

@singleton
class Settings(BaseSettings):
    UPLOAD_FOLDER: str = Field(default_factory=lambda: os.getenv("UPLOAD_FOLDER", "/tmp/playground"))
    MAX_UPLOAD_SIZE: int = 1024 * 1024 * 100
    EXECUTION_TIMEOUT: int = Field(default_factory=lambda: int(os.getenv("EXECUTION_TIMEOUT", "5")))
    ALLOWED_ORIGINS: List[str] = Field(default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://etlas.vercel.app").split(","))
    CLEANUP_AFTER_RUN: bool = Field(default_factory=lambda: os.getenv("CLEANUP_AFTER_RUN", "True").lower() == "true")
    OPENAI_API_KEY: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    MODEL_NAME: str = Field(default_factory=lambda: os.getenv("MODEL_NAME", "o4-mini"))
    DATABASE_URL: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./app.db"))

settings:Settings = Settings()