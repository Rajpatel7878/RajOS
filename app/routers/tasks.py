from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import SessionLocal
from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.security.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    new_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority or "normal",
        due_date=task.due_date,
        user_id=user.id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Fire push notification (non-blocking, best-effort)
    try:
        from app.services.push_service import push_service
        push_service.send_to_user(
            user.id, db,
            title="📋 New Task Added",
            body=f'"{task.title}" has been added to your tasks.',
            url="/tasks",
        )
    except Exception:
        pass

    return new_task


@router.get("/")
def get_tasks(
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Task).filter(Task.user_id == user.id)
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if priority:
        query = query.filter(Task.priority == priority)
    return query.order_by(Task.due_date.asc().nullslast(), Task.id.desc()).all()


@router.get("/summary")
def get_task_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Returns task counts — used by notification bell and dashboard."""
    now = datetime.utcnow()
    total = db.query(Task).filter(Task.user_id == user.id).count()
    completed = db.query(Task).filter(
        Task.user_id == user.id, Task.completed == True
    ).count()
    pending = total - completed
    overdue = db.query(Task).filter(
        Task.user_id == user.id,
        Task.completed == False,
        Task.due_date != None,
        Task.due_date < now,
    ).count()
    due_today = db.query(Task).filter(
        Task.user_id == user.id,
        Task.completed == False,
        Task.due_date >= now.replace(hour=0, minute=0, second=0),
        Task.due_date <= now.replace(hour=23, minute=59, second=59),
    ).count()

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue,
        "due_today": due_today,
    }


@router.get("/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(
        Task.id == task_id, Task.user_id == user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}")
def update_task(
    task_id: int,
    update: TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(
        Task.id == task_id, Task.user_id == user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if update.title is not None:
        task.title = update.title
    if update.description is not None:
        task.description = update.description
    if update.priority is not None:
        task.priority = update.priority
    if update.due_date is not None:
        task.due_date = update.due_date

    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}/complete")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(
        Task.id == task_id, Task.user_id == user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = True
    task.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(task)

    # Send push: task completed
    try:
        from app.services.push_service import push_service
        remaining = db.query(Task).filter(
            Task.user_id == user.id, Task.completed == False
        ).count()
        push_service.send_to_user(
            user.id, db,
            title="✅ Task Completed!",
            body=f'"{task.title}" done. {remaining} tasks remaining.',
            url="/tasks",
        )
    except Exception:
        pass

    return {
        "message": "Task completed successfully",
        "task_id": task.id,
        "completed_at": task.completed_at,
    }


@router.patch("/{task_id}/toggle")
def toggle_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Toggle a task between completed and pending."""
    task = db.query(Task).filter(
        Task.id == task_id, Task.user_id == user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    task.completed_at = datetime.utcnow() if task.completed else None
    db.commit()
    db.refresh(task)

    return {
        "message": f"Task marked as {'completed' if task.completed else 'pending'}",
        "task_id": task.id,
        "completed": task.completed,
        "completed_at": task.completed_at,
    }


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(
        Task.id == task_id, Task.user_id == user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
