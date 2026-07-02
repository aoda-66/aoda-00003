from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "文博文物数字化管理系统"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = f"sqlite:///{Path(__file__).resolve().parent.parent.parent / 'data' / 'museum.db'}"
    
    SECRET_KEY: str = "museum_secret_key_20240101_secure_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    IMAGE_STORAGE_DIR: str = str(Path(__file__).resolve().parent.parent.parent / 'data' / 'images')
    SCAN_STORAGE_DIR: str = str(Path(__file__).resolve().parent.parent.parent / 'data' / 'scans')
    
    ALLOWED_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()