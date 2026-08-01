from sqlalchemy import Column, Integer, String, Boolean
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
