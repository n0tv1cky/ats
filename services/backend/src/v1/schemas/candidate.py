"""Candidate schemas."""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class CandidateBase(BaseModel):
    """Base candidate schema."""
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    location: Optional[str] = None
    years_of_experience: Optional[int] = None
    current_salary: Optional[float] = None
    expected_salary: Optional[float] = None
    status: str = "eligible"
    source: Optional[str] = None
    objective_rating: Optional[float] = None
    remarks: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Candidate creation schema."""
    bucket_ids: List[int] = []
    skill_ids: List[int] = []


class CandidateUpdate(BaseModel):
    """Candidate update schema."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    years_of_experience: Optional[int] = None
    current_salary: Optional[float] = None
    expected_salary: Optional[float] = None
    status: Optional[str] = None
    source: Optional[str] = None
    objective_rating: Optional[float] = None
    remarks: Optional[str] = None
    bucket_ids: Optional[List[int]] = None
    skill_ids: Optional[List[int]] = None


class CandidateResponse(CandidateBase):
    """Candidate response schema."""
    id: int
    resume_url: Optional[str] = None
    uploaded_by: int
    upload_date: datetime
    created_at: datetime
    updated_at: Optional[datetime]
    bucket_ids: List[int] = []
    skill_ids: List[int] = []
    
    class Config:
        from_attributes = True


class CandidateListResponse(BaseModel):
    """Candidate list response with pagination."""
    data: List[CandidateResponse]
    pagination: dict
    
    class Config:
        from_attributes = True

