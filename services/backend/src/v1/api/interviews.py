"""Interview endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ..db.base import get_db
from ..models.interview import InterviewRound
from ..models.candidate import Candidate
from ..schemas.interview import (
    InterviewRoundCreate,
    InterviewRoundUpdate,
    InterviewRoundResponse,
)
from ..schemas.common import PaginationParams
from ..dependencies import get_current_user, get_hr_user
from ..models.user import User

router = APIRouter()


def calculate_pagination(total: int, page: int, page_size: int) -> dict:
    """Calculate pagination metadata."""
    total_pages = (total + page_size - 1) // page_size
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


@router.post("", response_model=InterviewRoundResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_data: InterviewRoundCreate,
    current_user: User = Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """Schedule a new interview."""
    # Verify candidate exists
    candidate = db.query(Candidate).filter(
        Candidate.id == interview_data.candidate_id,
        Candidate.deleted_at == None
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # Check if round already exists
    existing = db.query(InterviewRound).filter(
        InterviewRound.candidate_id == interview_data.candidate_id,
        InterviewRound.round_number == interview_data.round_number,
        InterviewRound.deleted_at == None
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview round already exists for this candidate",
        )
    
    # Create interview
    interview = InterviewRound(
        **interview_data.model_dump(),
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    return InterviewRoundResponse.model_validate(interview)


@router.get("", response_model=dict)
async def list_interviews(
    pagination: PaginationParams = Depends(),
    candidate_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List interviews with pagination."""
    query = db.query(InterviewRound).filter(InterviewRound.deleted_at == None)
    
    # Apply filters
    if candidate_id:
        query = query.filter(InterviewRound.candidate_id == candidate_id)
    
    if status_filter:
        query = query.filter(InterviewRound.status == status_filter)
    
    # For interviewers, only show their interviews
    if current_user.role == "interviewer":
        query = query.filter(InterviewRound.interviewer_id == current_user.id)
    
    # Get total count
    total = query.count()
    
    # Apply sorting
    sort_column = getattr(InterviewRound, pagination.sort_by, InterviewRound.created_at)
    if pagination.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.page_size
    interviews = query.offset(offset).limit(pagination.page_size).all()
    
    return {
        "data": [InterviewRoundResponse.model_validate(i) for i in interviews],
        "pagination": calculate_pagination(total, pagination.page, pagination.page_size),
    }


@router.get("/{interview_id}", response_model=InterviewRoundResponse)
async def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get interview by ID."""
    query = db.query(InterviewRound).filter(
        InterviewRound.id == interview_id,
        InterviewRound.deleted_at == None
    )
    
    # For interviewers, only allow access to their interviews
    if current_user.role == "interviewer":
        query = query.filter(InterviewRound.interviewer_id == current_user.id)
    
    interview = query.first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    return InterviewRoundResponse.model_validate(interview)


@router.put("/{interview_id}", response_model=InterviewRoundResponse)
async def update_interview(
    interview_id: int,
    interview_data: InterviewRoundUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update interview."""
    query = db.query(InterviewRound).filter(
        InterviewRound.id == interview_id,
        InterviewRound.deleted_at == None
    )
    
    # For interviewers, only allow updating their interviews
    if current_user.role == "interviewer":
        query = query.filter(InterviewRound.interviewer_id == current_user.id)
    
    interview = query.first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    # Update fields
    update_data = interview_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interview, field, value)
    
    db.commit()
    db.refresh(interview)
    
    return InterviewRoundResponse.model_validate(interview)


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(
    interview_id: int,
    hard_delete: bool = Query(False),
    current_user: User = Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """Delete interview (soft delete by default)."""
    interview = db.query(InterviewRound).filter(
        InterviewRound.id == interview_id,
        InterviewRound.deleted_at == None
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    
    if hard_delete and current_user.role == "admin":
        db.delete(interview)
    else:
        interview.deleted_at = datetime.utcnow()
    
    db.commit()
    return None

