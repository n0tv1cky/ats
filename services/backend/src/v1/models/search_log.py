"""Search log model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base


class SearchLog(Base):
    """Search log model."""
    
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    search_query = Column(String, nullable=True)
    search_filters = Column(JSON, nullable=True)
    results_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        Index("idx_search_logs_user", "user_id"),
        Index("idx_search_logs_created_at", "created_at"),
    )

