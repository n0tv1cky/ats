"""Candidate models."""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from ..db.base import Base


class Candidate(Base):
    """Candidate model."""
    
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    phone_number = Column(String, nullable=True)
    location = Column(String, nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    current_salary = Column(Float, nullable=True)
    expected_salary = Column(Float, nullable=True)
    resume_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default="eligible")  # eligible, rejected, hired
    source = Column(String, nullable=True)  # linkedin, naukri, referral
    objective_rating = Column(Float, nullable=True)
    remarks = Column(Text, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    uploader = relationship("User", back_populates="uploaded_candidates")
    buckets = relationship("CandidateBucket", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("InterviewRound", back_populates="candidate", cascade="all, delete-orphan")
    rejections = relationship("Rejection", back_populates="candidate")
    notes = relationship("CandidateNote", back_populates="candidate", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_candidates_status", "status"),
        Index("idx_candidates_uploaded_by", "uploaded_by"),
        Index("idx_candidates_created_at", "created_at"),
    )


class CandidateBucket(Base):
    """Junction table for candidates and buckets."""
    
    __tablename__ = "candidate_buckets"
    
    candidate_id = Column(Integer, ForeignKey("candidates.id"), primary_key=True)
    bucket_id = Column(Integer, ForeignKey("resume_buckets.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="buckets")
    bucket = relationship("ResumeBucket", back_populates="candidates")
    
    __table_args__ = (
        Index("idx_candidate_buckets_candidate", "candidate_id"),
        Index("idx_candidate_buckets_bucket", "bucket_id"),
        Index("idx_candidate_buckets_unique", "candidate_id", "bucket_id", unique=True),
    )


class CandidateSkill(Base):
    """Junction table for candidates and skills."""
    
    __tablename__ = "candidate_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    proficiency_level = Column(String, nullable=True)  # beginner, intermediate, advanced, expert
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="skills")
    skill = relationship("Skill", back_populates="candidates")
    
    __table_args__ = (
        Index("idx_candidate_skills_candidate", "candidate_id"),
        Index("idx_candidate_skills_skill", "skill_id"),
        Index("idx_candidate_skills_unique", "candidate_id", "skill_id", unique=True),
    )


class CandidateNote(Base):
    """Notes for candidates."""
    
    __tablename__ = "candidate_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="notes")
    user = relationship("User")
    
    __table_args__ = (
        Index("idx_candidate_notes_candidate", "candidate_id"),
        Index("idx_candidate_notes_user", "user_id"),
    )

