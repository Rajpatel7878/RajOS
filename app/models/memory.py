from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)

    key = Column(String, nullable=False)

    value = Column(String, nullable=False)

    content = Column(Text, nullable=True)

    memory_type = Column(
        String,
        default="preference",
        nullable=False
    )

    source = Column(
        String,
        default="explicit_user",
        nullable=False
    )

    confidence = Column(
        String,
        default="high",
        nullable=False
    )

    importance = Column(
        String,
        default="medium",
        nullable=False
    )

    status = Column(
        String,
        default="active",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    last_accessed_at = Column(
        DateTime,
        nullable=True
    )

    access_count = Column(
        Integer,
        default=0,
        nullable=False
    )

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship(
        "User",
        back_populates="memories"
    )
