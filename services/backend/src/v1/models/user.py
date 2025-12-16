"""User model."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

from ..db.base import Base


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, interviewer, hr
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)  # For non-OAuth users
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    uploaded_candidates = relationship("Candidate", back_populates="uploader")
    interviews = relationship("InterviewRound", back_populates="interviewer")
    feedbacks = relationship("InterviewFeedback", back_populates="interviewer")
    rejections = relationship("Rejection", back_populates="rejected_by_user")
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    
    __table_args__ = (
        Index("idx_users_oauth", "oauth_provider", "oauth_id", unique=True),
        Index("idx_users_active", "is_active"),
    )

