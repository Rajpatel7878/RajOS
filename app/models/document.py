from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String,
        nullable=False
    )

    title = Column(
        String,
        nullable=True
    )

    content = Column(
        Text,
        nullable=False
    )

    mime_type = Column(
        String,
        default="text/plain",
        nullable=False
    )

    file_size = Column(
        Integer,
        default=0,
        nullable=False
    )

    status = Column(
        String,
        default="ready",
        nullable=False
    )

    processed_at = Column(
        DateTime,
        nullable=True
    )

    error_message = Column(
        Text,
        nullable=True
    )

    metadata_json = Column(
        Text,
        nullable=True
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

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    user = relationship(
        "User"
    )
