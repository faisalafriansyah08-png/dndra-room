from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application
    APP_NAME: str = "Hotel Booking System"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    EMAIL_FROM_NAME: str = "Hotel Booking"
    
    # Payment - Xendit
    XENDIT_API_KEY: str = ""
    XENDIT_WEBHOOK_TOKEN: str = ""
    XENDIT_CALLBACK_URL: str = ""
    
    # Payment - Midtrans
    MIDTRANS_SERVER_KEY: str = ""
    MIDTRANS_CLIENT_KEY: str = ""
    MIDTRANS_IS_PRODUCTION: bool = False
    
    # URLs
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 5242880
    UPLOAD_DIR: str = "./uploads"
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()