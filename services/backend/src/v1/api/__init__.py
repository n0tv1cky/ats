"""API endpoints."""
from fastapi import APIRouter

from .auth import router as auth_router
from .candidates import router as candidates_router
from .interviews import router as interviews_router
from .feedback import router as feedback_router
from .health import router as health_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(candidates_router, prefix="/candidates", tags=["candidates"])
api_router.include_router(interviews_router, prefix="/interviews", tags=["interviews"])
api_router.include_router(feedback_router, prefix="/feedback", tags=["feedback"])

