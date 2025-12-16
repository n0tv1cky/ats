"""Interview schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InterviewRoundBase(BaseModel):
    """Base interview round schema."""
    candidate_id: int
    round_number: int  # 0-4
    round_name: str
    scheduled_date: Optional[datetime] = None
    duration: Optional[int] = None
    interviewer_id: int
    meeting_link: Optional[str] = None
    current_ctc: Optional[float] = None
    expected_ctc: Optional[float] = None
    notice_period: Optional[int] = None


class InterviewRoundCreate(InterviewRoundBase):
    """Interview round creation schema."""
    status: str = "scheduled"


class InterviewRoundUpdate(BaseModel):
    """Interview round update schema."""
    status: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    duration: Optional[int] = None
    meeting_link: Optional[str] = None
    meeting_notes_url: Optional[str] = None
    current_ctc: Optional[float] = None
    expected_ctc: Optional[float] = None
    notice_period: Optional[int] = None


class InterviewRoundResponse(InterviewRoundBase):
    """Interview round response schema."""
    id: int
    status: str
    meeting_notes_url: Optional[str] = None
    calendar_event_id: Optional[str] = None
    calendar_synced_at: Optional[datetime] = None
    calendar_deleted_externally: bool = False
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class InterviewFeedbackBase(BaseModel):
    """Base interview feedback schema."""
    interview_round_id: int
    technical_proficiency_score: int  # 0-100
    attitude_score: int  # 0-100
    code_cleanliness_score: int  # 0-100
    communication_score: int  # 0-100
    feedback_text: Optional[str] = None
    decision: str  # eligible, rejected


class InterviewFeedbackCreate(InterviewFeedbackBase):
    """Interview feedback creation schema."""
    pass


class InterviewFeedbackResponse(InterviewFeedbackBase):
    """Interview feedback response schema."""
    id: int
    interviewer_id: int
    overall_rating: float
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

