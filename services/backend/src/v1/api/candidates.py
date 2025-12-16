"""Candidate endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List

from ..db.base import get_db
from ..models.candidate import Candidate, CandidateBucket, CandidateSkill
from ..models.bucket import ResumeBucket
from ..models.skill import Skill
from ..schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListResponse,
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


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    current_user: User = Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """Create a new candidate."""
    # Check if email already exists
    existing = db.query(Candidate).filter(
        Candidate.email == candidate_data.email,
        Candidate.deleted_at == None
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate with this email already exists",
        )
    
    # Create candidate
    candidate = Candidate(
        **candidate_data.model_dump(exclude={"bucket_ids", "skill_ids"}),
        uploaded_by=current_user.id,
    )
    db.add(candidate)
    db.flush()
    
    # Add buckets
    if candidate_data.bucket_ids:
        buckets = db.query(ResumeBucket).filter(ResumeBucket.id.in_(candidate_data.bucket_ids)).all()
        for bucket in buckets:
            db.add(CandidateBucket(candidate_id=candidate.id, bucket_id=bucket.id))
    
    # Add skills
    if candidate_data.skill_ids:
        skills = db.query(Skill).filter(Skill.id.in_(candidate_data.skill_ids)).all()
        for skill in skills:
            db.add(CandidateSkill(candidate_id=candidate.id, skill_id=skill.id))
    
    db.commit()
    db.refresh(candidate)
    
    # Get bucket and skill IDs
    bucket_ids = [cb.bucket_id for cb in candidate.buckets]
    skill_ids = [cs.skill_id for cs in candidate.skills]
    
    response = CandidateResponse.model_validate(candidate)
    response.bucket_ids = bucket_ids
    response.skill_ids = skill_ids
    
    return response


@router.get("", response_model=CandidateListResponse)
async def list_candidates(
    pagination: PaginationParams = Depends(),
    status_filter: Optional[str] = Query(None, alias="status"),
    bucket_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List candidates with pagination and filters."""
    query = db.query(Candidate).filter(Candidate.deleted_at == None)
    
    # Apply filters
    if status_filter:
        query = query.filter(Candidate.status == status_filter)
    
    if bucket_id:
        query = query.join(CandidateBucket).filter(CandidateBucket.bucket_id == bucket_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Candidate.name.ilike(search_term),
                Candidate.email.ilike(search_term),
                Candidate.remarks.ilike(search_term) if Candidate.remarks else False,
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply sorting
    sort_column = getattr(Candidate, pagination.sort_by, Candidate.created_at)
    if pagination.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.page_size
    candidates = query.offset(offset).limit(pagination.page_size).all()
    
    # Build response
    candidate_responses = []
    for candidate in candidates:
        bucket_ids = [cb.bucket_id for cb in candidate.buckets]
        skill_ids = [cs.skill_id for cs in candidate.skills]
        response = CandidateResponse.model_validate(candidate)
        response.bucket_ids = bucket_ids
        response.skill_ids = skill_ids
        candidate_responses.append(response)
    
    return {
        "data": candidate_responses,
        "pagination": calculate_pagination(total, pagination.page, pagination.page_size),
    }


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get candidate by ID."""
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.deleted_at == None
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    bucket_ids = [cb.bucket_id for cb in candidate.buckets]
    skill_ids = [cs.skill_id for cs in candidate.skills]
    response = CandidateResponse.model_validate(candidate)
    response.bucket_ids = bucket_ids
    response.skill_ids = skill_ids
    
    return response


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    current_user: User = Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """Update candidate."""
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.deleted_at == None
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    # Update fields
    update_data = candidate_data.model_dump(exclude_unset=True, exclude={"bucket_ids", "skill_ids"})
    for field, value in update_data.items():
        setattr(candidate, field, value)
    
    # Update buckets if provided
    if candidate_data.bucket_ids is not None:
        db.query(CandidateBucket).filter(CandidateBucket.candidate_id == candidate_id).delete()
        if candidate_data.bucket_ids:
            buckets = db.query(ResumeBucket).filter(ResumeBucket.id.in_(candidate_data.bucket_ids)).all()
            for bucket in buckets:
                db.add(CandidateBucket(candidate_id=candidate.id, bucket_id=bucket.id))
    
    # Update skills if provided
    if candidate_data.skill_ids is not None:
        db.query(CandidateSkill).filter(CandidateSkill.candidate_id == candidate_id).delete()
        if candidate_data.skill_ids:
            skills = db.query(Skill).filter(Skill.id.in_(candidate_data.skill_ids)).all()
            for skill in skills:
                db.add(CandidateSkill(candidate_id=candidate.id, skill_id=skill.id))
    
    db.commit()
    db.refresh(candidate)
    
    bucket_ids = [cb.bucket_id for cb in candidate.buckets]
    skill_ids = [cs.skill_id for cs in candidate.skills]
    response = CandidateResponse.model_validate(candidate)
    response.bucket_ids = bucket_ids
    response.skill_ids = skill_ids
    
    return response


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: int,
    hard_delete: bool = Query(False),
    current_user: User = Depends(get_hr_user),
    db: Session = Depends(get_db)
):
    """Delete candidate (soft delete by default)."""
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.deleted_at == None
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )
    
    if hard_delete and current_user.role == "admin":
        db.delete(candidate)
    else:
        from datetime import datetime
        candidate.deleted_at = datetime.utcnow()
    
    db.commit()
    return None

