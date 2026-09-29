from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from app.security.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    new_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority or "normal",
        category=task.category,
        tags=task.tags,
        estimated_duration=task.estimated_duration,
        due_date=task.due_date,
        parent_task_id=task.parent_task_id,
        user_id=user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(Task).filter(Task.user_id == user.id)
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if category:
        query = query.filter(Task.category == category)
    if priority:
        query = query.filter(Task.priority == priority)
    return query.order_by(Task.id.desc()).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.category is not None:
        task.category = task_update.category
    if task_update.tags is not None:
        task.tags = task_update.tags
    if task_update.estimated_duration is not None:
        task.estimated_duration = task_update.estimated_duration
    if task_update.actual_duration is not None:
        task.actual_duration = task_update.actual_duration
    if task_update.due_date is not None:
        task.due_date = task_update.due_date
    if task_update.completed is not None:
        task.completed = task_update.completed
        if task_update.completed and not task.completed_at:
            task.completed_at = datetime.utcnow()
        elif not task_update.completed:
            task.completed_at = None

    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}/complete")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = True
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return {
        "message": "Task completed successfully",
        "task_id": task.id,
        "completed_at": task.completed_at
    }


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted", "task_id": task_id}
