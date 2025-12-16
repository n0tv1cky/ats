"""Authentication schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    """Token schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

