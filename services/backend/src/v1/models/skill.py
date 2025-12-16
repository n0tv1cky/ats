"""Skill model."""
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base


class Skill(Base):
    """Skill model."""
    
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=True, index=True)  # technical, soft, language, framework, tool
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    candidates = relationship("CandidateSkill", back_populates="skill")

