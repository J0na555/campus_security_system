import os
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    PROJECT_NAME: str = "Campus Security System"
    VERSION: str = "1.1.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./campus_security.db")

settings = Settings()
