from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.task import Task
from app.schemas.task_schema import TaskCreate
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
    user: User = Depends(get_current_user)
):

    new_task = Task(
        title=task.title,
        description=task.description,
        user_id=user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("/")
def get_tasks(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    return db.query(Task).filter(
        Task.user_id == user.id
    ).all()


@router.get("/{task_id}")
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
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


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
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted"
    }


@router.patch("/{task_id}/complete")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    from datetime import datetime

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user.id
    ).first()


    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )


    task.completed = True
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)


    return {
        "message": "Task completed successfully",
        "task_id": task.id,
        "completed_at": task.completed_at
    }
