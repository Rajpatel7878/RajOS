from sqlalchemy import Column, Index, Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.database.connection import Base


class SearchHistory(Base):
    __tablename__ = "search_history"
    __table_args__ = (
        Index("ix_search_history_user_searched", "user_id", "searched_at"),
    )

    id = Column(Integer, primary_key=True, index=True)

    query = Column(String, nullable=False)

    search_type = Column(String, default="all")

    resource_types = Column(String, nullable=True)

    result_count = Column(Integer, default=0, nullable=False)

    searched_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
