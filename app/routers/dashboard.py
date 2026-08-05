from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.task import Task
from app.models.note import Note
from app.models.memory import Memory
from app.models.user import User
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    total_tasks = db.query(Task).filter(
        Task.user_id == user.id
    ).count()

    completed_tasks = db.query(Task).filter(
        Task.user_id == user.id,
        Task.completed == True
    ).count()

    total_notes = db.query(Note).filter(
        Note.user_id == user.id
    ).count()

    total_memories = db.query(Memory).filter(
        Memory.user_id == user.id
    ).count()

    return {
        "tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "notes": total_notes,
        "memories": total_memories
    }

from sqlalchemy import desc

@router.get("/activity")
def dashboard_activity(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    tasks = db.query(Task).filter(
        Task.user_id == user.id
    ).order_by(desc(Task.id)).limit(5).all()

    notes = db.query(Note).filter(
        Note.user_id == user.id
    ).order_by(desc(Note.id)).limit(5).all()

    memories = db.query(Memory).filter(
        Memory.user_id == user.id
    ).order_by(desc(Memory.id)).limit(5).all()

    activity = []

    for t in tasks:
        activity.append({
            "type": "task",
            "title": t.title
        })

    for n in notes:
        activity.append({
            "type": "note",
            "title": n.title
        })

    for m in memories:
        activity.append({
            "type": "memory",
            "title": m.key
        })

    return activity
