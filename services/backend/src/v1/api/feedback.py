"""Feedback endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..models.interview import InterviewRound, InterviewFeedback
from ..schemas.interview import InterviewFeedbackCreate, InterviewFeedbackResponse
from ..dependencies import get_current_user
from ..models.user import User

router = APIRouter()


@router.post("", response_model=InterviewFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: InterviewFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit interview feedback."""
    # Verify interview exists and belongs to interviewer
    interview = db.query(InterviewRound).filter(
        InterviewRound.id == feedback_data.interview_round_id,
        InterviewRound.interviewer_id == current_user.id,
        InterviewRound.deleted_at == None
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found or you don't have permission",
        )
    
    # Check if feedback already exists
    existing = db.query(InterviewFeedback).filter(
        InterviewFeedback.interview_round_id == feedback_data.interview_round_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback already submitted for this interview",
        )
    
    # Calculate overall rating
    overall_rating = (
        feedback_data.technical_proficiency_score * 0.4 +
        feedback_data.attitude_score * 0.2 +
        feedback_data.code_cleanliness_score * 0.2 +
        feedback_data.communication_score * 0.2
    )
    
    # Create feedback
    feedback = InterviewFeedback(
        **feedback_data.model_dump(),
        interviewer_id=current_user.id,
        overall_rating=overall_rating,
    )
    db.add(feedback)
    
    # Update interview status
    interview.status = "completed"
    
    db.commit()
    db.refresh(feedback)
    
    return InterviewFeedbackResponse.model_validate(feedback)


@router.get("/{interview_id}", response_model=InterviewFeedbackResponse)
async def get_feedback(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback for an interview."""
    feedback = db.query(InterviewFeedback).filter(
        InterviewFeedback.interview_round_id == interview_id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )
    
    # Check permissions
    interview = db.query(InterviewRound).filter(
        InterviewRound.id == interview_id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    # Interviewers can only see their own feedback, HR and admin can see all
    if current_user.role == "interviewer" and feedback.interviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    
    return InterviewFeedbackResponse.model_validate(feedback)

