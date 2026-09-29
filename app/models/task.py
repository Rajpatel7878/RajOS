from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, backref
from datetime import datetime

from app.database.connection import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default="normal")  # "low", "normal", "high"
    category = Column(String, nullable=True)     # e.g. "Work", "College", "Personal"
    tags = Column(String, nullable=True)         # comma-separated tags or json
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    actual_duration = Column(Integer, nullable=True)     # in minutes
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    metadata_json = Column(JSON, nullable=True)

    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="tasks")
    subtasks = relationship("Task", backref=backref("parent", remote_side=[id]), cascade="all, delete-orphan")

