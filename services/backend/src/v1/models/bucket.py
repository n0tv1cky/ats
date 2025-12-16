"""Bucket model."""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base


class ResumeBucket(Base):
    """Resume bucket model."""
    
    __tablename__ = "resume_buckets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # AI, Full Stack, DevOps, etc.
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidates = relationship("CandidateBucket", back_populates="bucket")

