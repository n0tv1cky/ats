"""User schemas."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str
    role: str  # admin, interviewer, hr


class UserCreate(UserBase):
    """User creation schema."""
    password: Optional[str] = None
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None


class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class User(UserResponse):
    """Full user schema."""
    pass

