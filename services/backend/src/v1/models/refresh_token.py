"""Refresh token model."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base


class RefreshToken(Base):
    """Refresh token model."""
    
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    __table_args__ = (
        Index("idx_refresh_tokens_user_revoked", "user_id", "revoked"),
    )

