"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..db.base import get_db
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_by_email,
)
from ..models.user import User
from ..models.refresh_token import RefreshToken
from ..schemas.auth import Token, LoginResponse
from ..schemas.user import UserResponse
from ..dependencies import get_current_user
from ..config import settings

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(email: str, password: str, db: Session = Depends(get_db)):
    """Login endpoint (OAuth will be added later)."""
    user = get_user_by_email(db, email)
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Store refresh token
    expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=expires_at,
    )
    db.add(db_refresh_token)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user).model_dump(),
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(token: str, db: Session = Depends(get_db)):
    """Refresh access token."""
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Check if token exists and is not revoked
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == token,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new access token
    access_token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    
    return {
        "access_token": access_token,
        "refresh_token": token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout endpoint - revokes refresh tokens."""
    # Revoke all refresh tokens for user
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked == False
    ).update({"revoked": True, "revoked_at": datetime.utcnow()})
    db.commit()
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

