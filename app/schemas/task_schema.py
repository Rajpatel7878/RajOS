from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "normal"
    category: Optional[str] = None
    tags: Optional[str] = None
    estimated_duration: Optional[int] = None  # in minutes
    due_date: Optional[datetime] = None
    parent_task_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    priority: Optional[str] = "normal"
    category: Optional[str] = None
    tags: Optional[str] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    parent_task_id: Optional[int] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
