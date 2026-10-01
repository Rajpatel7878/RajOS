from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.task import Task
from app.models.note import Note
from app.models.memory import Memory
from app.models.user import User
from app.security.dependencies import get_current_user
from app.productivity.workload_service import workload_service
from app.productivity.recommendation_engine import recommendation_engine


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    total_tasks = db.query(Task).filter(Task.user_id == user.id).count()
    completed_tasks = db.query(Task).filter(Task.user_id == user.id, Task.completed == True).count()
    total_notes = db.query(Note).filter(Note.user_id == user.id).count()
    total_memories = db.query(Memory).filter(Memory.user_id == user.id).count()

    now = datetime.utcnow()
    overdue_count = db.query(Task).filter(
        Task.user_id == user.id,
        Task.completed == False,
        Task.due_date < now
    ).count()

    comp_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0
    brief = workload_service.get_daily_brief(db, user.id)

    return {
        "tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": total_tasks - completed_tasks,
        "overdue_tasks": overdue_count,
        "completion_rate": comp_rate,
        "notes": total_notes,
        "memories": total_memories,
        "recommended_focus": brief.get("recommended_focus", []),
        "quick_wins": brief.get("quick_wins", [])
    }


@router.get("/activity")
def dashboard_activity(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    tasks = db.query(Task).filter(Task.user_id == user.id).order_by(desc(Task.id)).limit(5).all()
    notes = db.query(Note).filter(Note.user_id == user.id).order_by(desc(Note.id)).limit(5).all()
    memories = db.query(Memory).filter(Memory.user_id == user.id).order_by(desc(Memory.id)).limit(5).all()

    activity = []
    for t in tasks:
        activity.append({
            "type": "task",
            "title": t.title,
            "completed": t.completed,
            "time": t.created_at.strftime("%b %d, %H:%M") if t.created_at else "Recently"
        })

    for n in notes:
        activity.append({
            "type": "note",
            "title": n.title,
            "time": n.created_at.strftime("%b %d, %H:%M") if n.created_at else "Recently"
        })

    for m in memories:
        activity.append({
            "type": "memory",
            "title": f"Memory: {m.key}",
            "time": m.created_at.strftime("%b %d, %H:%M") if m.created_at else "Recently"
        })

    return activity
