"""Rejection models."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base


class Rejection(Base):
    """Rejection model."""
    
    __tablename__ = "rejections"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    rejected_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    rejection_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    rejection_reason = Column(Text, nullable=True)
    stage = Column(String, nullable=False)  # resume_screening, interview_round
    round_number = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="rejections")
    rejected_by_user = relationship("User", back_populates="rejections")
    reapplication_alerts = relationship("ReapplicationAlert", back_populates="original_rejection")
    
    __table_args__ = (
        Index("idx_rejections_candidate", "candidate_id"),
        Index("idx_rejections_date", "rejection_date"),
    )


class ReapplicationAlert(Base):
    """Reapplication alert model (Phase 2)."""
    
    __tablename__ = "reapplication_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    original_rejection_id = Column(Integer, ForeignKey("rejections.id"), nullable=False)
    reapplication_date = Column(DateTime(timezone=True), server_default=func.now())
    notified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("Candidate")
    original_rejection = relationship("Rejection", back_populates="reapplication_alerts")

