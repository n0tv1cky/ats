"""Notification model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base


class Notification(Base):
    """Notification model."""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # interview_scheduled, feedback_submitted, etc.
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    related_resource_type = Column(String, nullable=True)  # candidate, interview, etc.
    related_resource_id = Column(Integer, nullable=True)
    read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    __table_args__ = (
        Index("idx_notifications_user_read", "user_id", "read"),
    )

