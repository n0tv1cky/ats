"""Configuration management for the ATS application."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    ENVIRONMENT: str = "development"
    API_VERSION: str = "v1"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/ats_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # JWT Authentication
    # Keep this separate from any API key; rotate for production
    JWT_SECRET_KEY: str  # Required - must be set via environment variable
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OAuth Google
    OAUTH_GOOGLE_CLIENT_ID: Optional[str] = None
    OAUTH_GOOGLE_CLIENT_SECRET: Optional[str] = None
    OAUTH_GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"
    
    # Google Workspace
    GOOGLE_CALENDAR_ID: str = "primary"
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = None
    CALENDAR_SYNC_INTERVAL: int = 7200  # seconds (2 hours)
    GOOGLE_SERVICE_ACCOUNT_KEY: Optional[str] = None
    
    # Storage
    GOOGLE_DRIVE_STORAGE_ENABLED: bool = True
    RESUME_STORAGE_PATH: str = "/resumes"
    
    # Email
    EMAIL_SERVICE: str = "sendgrid"  # or ses
    SENDGRID_API_KEY: Optional[str] = None
    AWS_SES_REGION: str = "us-east-1"
    
    # OpenAI (Phase 2)
    OPENAI_API_KEY: Optional[str] = None  # Must be set via environment variable
    OPENAI_MODEL: str = "gpt-5.2"
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = "application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    MAX_BATCH_SIZE: int = 50
    
    # Initial Admin User
    ADMIN_EMAIL: str = "admin@ucube.ai"
    ADMIN_PASSWORD: str = "admin"
    ADMIN_USERNAME: str = "admin"
    
    class Config:
        env_file = [".env.dev", ".env.prod"]
        case_sensitive = False


settings = Settings()

