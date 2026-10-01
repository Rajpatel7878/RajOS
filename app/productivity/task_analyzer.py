from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.task import Task
from app.productivity.priority_engine import priority_engine


class TaskAnalyzer:
    """
    Task Analysis Service providing smart categorizations and insights.
    Strictly isolated per user_id.
    """

    def analyze_user_tasks(self, db: Session, user_id: int) -> Dict[str, Any]:
        now = datetime.utcnow()
        tasks = db.query(Task).filter(Task.user_id == user_id).all()

        total = len(tasks)
        completed_tasks = [t for t in tasks if t.completed]
        pending_tasks = [t for t in tasks if not t.completed]

        completed_count = len(completed_tasks)
        pending_count = len(pending_tasks)
        completion_rate = round((completed_count / total * 100), 1) if total > 0 else 0.0

        overdue_list = []
        due_soon_list = []
        stale_list = []
        quick_wins_list = []
        heavy_tasks_list = []
        high_impact_list = []
        unscheduled_list = []

        # Analyze each pending task
        for t in pending_tasks:
            # Count subtasks if any
            subtasks_count = db.query(Task).filter(Task.parent_task_id == t.id, Task.user_id == user_id).count()
            p_analysis = priority_engine.analyze_priority(t, subtasks_count=subtasks_count)

            task_summary = {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "computed_priority": p_analysis["computed_priority"],
                "priority_score": p_analysis["priority_score"],
                "category": t.category,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "estimated_duration": t.estimated_duration,
                "reasons": p_analysis["reasons"]
            }

            # Overdue
            if t.due_date and t.due_date < now:
                overdue_list.append(task_summary)

            # Due Soon (within 3 days)
            elif t.due_date and t.due_date <= now + timedelta(days=3):
                due_soon_list.append(task_summary)

            # Unscheduled (High priority/urgent without due date)
            if not t.due_date and (t.priority == "high" or p_analysis["priority_score"] >= 50):
                unscheduled_list.append(task_summary)

            # Stale (pending > 7 days with no updates)
            if t.created_at and (now - t.created_at).days >= 7:
                stale_list.append(task_summary)

            # Quick wins (<= 30 minutes)
            if t.estimated_duration and t.estimated_duration <= 30:
                quick_wins_list.append(task_summary)
            elif not t.estimated_duration and len(t.title) < 40 and not t.description:
                quick_wins_list.append(task_summary)

            # Heavy tasks (>= 120 minutes)
            if t.estimated_duration and t.estimated_duration >= 120:
                heavy_tasks_list.append(task_summary)

            # High impact (Score >= 60 or blocking subtasks)
            if p_analysis["priority_score"] >= 60 or subtasks_count > 0:
                high_impact_list.append(task_summary)

        return {
            "total_tasks": total,
            "completed_tasks": completed_count,
            "pending_tasks": pending_count,
            "completion_rate": completion_rate,
            "overdue_count": len(overdue_list),
            "due_soon_count": len(due_soon_list),
            "overdue_tasks": overdue_list,
            "due_soon_tasks": due_soon_list,
            "stale_tasks": stale_list,
            "quick_wins": quick_wins_list,
            "heavy_tasks": heavy_tasks_list,
            "high_impact_tasks": high_impact_list,
            "unscheduled_tasks": unscheduled_list
        }


task_analyzer = TaskAnalyzer()
