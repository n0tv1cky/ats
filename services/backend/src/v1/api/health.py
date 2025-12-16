"""Health check endpoints."""
from fastapi import APIRouter
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..db.base import get_db
from ..config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.API_VERSION,
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check endpoint - verifies database connection."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "disconnected",
            "error": str(e),
        }

