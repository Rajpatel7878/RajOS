from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True)

    email = Column(String, unique=True)

    password = Column(String)

    phone_number = Column(
        String,
        nullable=True
    )

    device_id = Column(
        String,
        nullable=True
    )

    notifications_enabled = Column(
        Boolean,
        default=True
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

    tasks = relationship(
        "Task",
        back_populates="user"
    )

    notes = relationship(
        "Note",
        back_populates="user"
    )

    memories = relationship(
        "Memory",
        back_populates="user"
    )

    documents = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    automations = relationship(
        "Automation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
