"""Audit log model."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base


class AuditLog(Base):
    """Audit log model."""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String, nullable=False, index=True)  # create, update, delete, view, login, logout
    resource_type = Column(String, nullable=False)  # candidate, interview, feedback, user
    resource_id = Column(Integer, nullable=True)
    changes = Column(JSON, nullable=True)  # before/after values
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
    )

