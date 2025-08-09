from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIREBASE_CREDENTIALS_JSON: Optional[str] = None
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Virtual Notice Board"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "https://yourdomain.com"]
    
    class Config:
        env_file = ".env"

settings = Settings()
