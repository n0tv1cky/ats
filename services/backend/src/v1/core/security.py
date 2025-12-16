"""Security utilities for authentication and authorization."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config import settings
from ..models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode a JWT token."""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return (
        db.query(User)
        .filter(
            User.email == email,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
        .first()
    )


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return (
        db.query(User)
        .filter(
            User.id == user_id,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
        .first()
    )


def require_role(allowed_roles: list[str]):
    """Decorator to require specific roles."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This will be implemented in dependencies
            return func(*args, **kwargs)
        return wrapper
    return decorator

