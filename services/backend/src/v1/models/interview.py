"""Interview models."""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base


class InterviewRound(Base):
    """Interview round model."""
    
    __tablename__ = "interview_rounds"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)  # 0-4
    round_name = Column(String, nullable=False)  # Phone Screen, Technical, Task Based, Behavioural
    status = Column(String, nullable=False, default="scheduled", index=True)  # scheduled, completed, cancelled
    scheduled_date = Column(DateTime(timezone=True), nullable=True, index=True)
    duration = Column(Integer, nullable=True)  # minutes
    interviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    meeting_link = Column(String, nullable=True)
    meeting_notes_url = Column(String, nullable=True)
    calendar_event_id = Column(String, nullable=True, index=True)
    calendar_synced_at = Column(DateTime(timezone=True), nullable=True)
    calendar_deleted_externally = Column(Boolean, default=False, nullable=False)
    current_ctc = Column(Float, nullable=True)
    expected_ctc = Column(Float, nullable=True)
    notice_period = Column(Integer, nullable=True)  # days
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    interviewer = relationship("User", back_populates="interviews")
    feedback = relationship("InterviewFeedback", back_populates="interview_round", uselist=False)
    
    __table_args__ = (
        Index("idx_interview_rounds_candidate_round", "candidate_id", "round_number", unique=True),
        Index("idx_interview_rounds_scheduled_date", "scheduled_date"),
    )


class InterviewFeedback(Base):
    """Interview feedback model."""
    
    __tablename__ = "interview_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_round_id = Column(Integer, ForeignKey("interview_rounds.id"), unique=True, nullable=False)
    interviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    technical_proficiency_score = Column(Integer, nullable=False)  # 0-100
    attitude_score = Column(Integer, nullable=False)  # 0-100
    code_cleanliness_score = Column(Integer, nullable=False)  # 0-100
    communication_score = Column(Integer, nullable=False)  # 0-100
    overall_rating = Column(Float, nullable=False)  # calculated
    feedback_text = Column(Text, nullable=True)
    decision = Column(String, nullable=False)  # eligible, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    interview_round = relationship("InterviewRound", back_populates="feedback")
    interviewer = relationship("User", back_populates="feedbacks")
    
    __table_args__ = (
        Index("idx_interview_feedback_round", "interview_round_id"),
        Index("idx_interview_feedback_interviewer", "interviewer_id"),
    )

