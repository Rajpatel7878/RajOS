from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.task import Task
from app.productivity.task_analyzer import task_analyzer
from app.productivity.priority_engine import priority_engine


class WorkloadService:
    """
    Workload Analysis, Daily Brief, Weekly Summary, and Productivity Trends Service.
    Operates strictly on user-authenticated data.
    """

    def get_workload_analysis(self, db: Session, user_id: int) -> Dict[str, Any]:
        tasks = db.query(Task).filter(Task.user_id == user_id).all()
        pending_tasks = [t for t in tasks if not t.completed]
        completed_tasks = [t for t in tasks if t.completed]

        # Category breakdown
        categories: Dict[str, int] = {}
        for t in pending_tasks:
            cat = t.category or "Uncategorized"
            categories[cat] = categories.get(cat, 0) + 1

        # Priority breakdown
        priorities: Dict[str, int] = {"high": 0, "normal": 0, "low": 0}
        for t in pending_tasks:
            p = (t.priority or "normal").lower()
            priorities[p] = priorities.get(p, 0) + 1

        # Total estimated workload in minutes
        total_est_minutes = sum(t.estimated_duration for t in pending_tasks if t.estimated_duration)

        return {
            "total_pending": len(pending_tasks),
            "total_completed": len(completed_tasks),
            "total_estimated_workload_minutes": total_est_minutes,
            "estimated_workload_formatted": f"{total_est_minutes // 60}h {total_est_minutes % 60}m" if total_est_minutes > 0 else "0m",
            "category_distribution": categories,
            "priority_distribution": priorities
        }

    def get_daily_brief(self, db: Session, user_id: int) -> Dict[str, Any]:
        analysis = task_analyzer.analyze_user_tasks(db, user_id)
        workload = self.get_workload_analysis(db, user_id)
        now = datetime.utcnow()

        # Tasks due today
        tasks_due_today = []
        pending_tasks = db.query(Task).filter(Task.user_id == user_id, Task.completed == False).all()
        for t in pending_tasks:
            if t.due_date and (t.due_date - now).total_seconds() >= 0 and t.due_date.date() == now.date():
                tasks_due_today.append({
                    "id": t.id,
                    "title": t.title,
                    "priority": t.priority,
                    "estimated_duration": t.estimated_duration
                })

        # Top 3 recommended focus tasks based on highest priority score
        all_scored = []
        for t in pending_tasks:
            sub_count = db.query(Task).filter(Task.parent_task_id == t.id).count()
            p_res = priority_engine.analyze_priority(t, subtasks_count=sub_count)
            all_scored.append({
                "id": t.id,
                "title": t.title,
                "score": p_res["priority_score"],
                "computed_priority": p_res["computed_priority"],
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "reasons": p_res["reasons"]
            })

        all_scored.sort(key=lambda x: x["score"], reverse=True)
        recommended_focus = all_scored[:3]

        return {
            "date": now.strftime("%Y-%m-%d"),
            "overdue_count": len(analysis["overdue_tasks"]),
            "overdue_tasks": analysis["overdue_tasks"],
            "due_today_count": len(tasks_due_today),
            "due_today_tasks": tasks_due_today,
            "recommended_focus": recommended_focus,
            "quick_wins": analysis["quick_wins"][:4],
            "total_estimated_workload": workload["estimated_workload_formatted"]
        }

    def get_weekly_summary(self, db: Session, user_id: int) -> Dict[str, Any]:
        now = datetime.utcnow()
        one_week_ago = now - timedelta(days=7)

        # Query tasks created/completed in last 7 days
        all_user_tasks = db.query(Task).filter(Task.user_id == user_id).all()
        created_this_week = [t for t in all_user_tasks if t.created_at and t.created_at >= one_week_ago]
        completed_this_week = [t for t in all_user_tasks if t.completed and t.completed_at and t.completed_at >= one_week_ago]

        completed_on_time = [
            t for t in completed_this_week
            if not t.due_date or (t.completed_at and t.completed_at <= t.due_date)
        ]

        overdue_count = len([t for t in all_user_tasks if not t.completed and t.due_date and t.due_date < now])
        total_eligible = len(created_this_week)
        comp_rate = round((len(completed_this_week) / total_eligible * 100), 1) if total_eligible > 0 else 0.0

        # Top categories
        categories: Dict[str, int] = {}
        for t in all_user_tasks:
            if t.category:
                categories[t.category] = categories.get(t.category, 0) + 1

        top_categories = dict(sorted(categories.items(), key=lambda item: item[1], reverse=True)[:3])

        return {
            "period": f"{one_week_ago.strftime('%b %d')} - {now.strftime('%b %d, %Y')}",
            "tasks_created": len(created_this_week),
            "tasks_completed": len(completed_this_week),
            "completed_on_time": len(completed_on_time),
            "overdue_count": overdue_count,
            "completion_rate": comp_rate,
            "top_categories": top_categories,
            "upcoming_important_tasks_count": len([t for t in all_user_tasks if not t.completed and t.priority == "high"])
        }

    def get_productivity_trends(self, db: Session, user_id: int) -> Dict[str, Any]:
        now = datetime.utcnow()
        all_user_tasks = db.query(Task).filter(Task.user_id == user_id).all()

        if len(all_user_tasks) < 3:
            return {
                "has_sufficient_data": False,
                "message": "Insufficient historical data for meaningful productivity trends. Keep using RajOS to unlock trends.",
                "daily_data": []
            }

        daily_data = []
        for i in range(6, -1, -1):
            day_date = (now - timedelta(days=i)).date()
            day_str = day_date.strftime("%a")

            created_on_day = len([t for t in all_user_tasks if t.created_at and t.created_at.date() == day_date])
            completed_on_day = len([t for t in all_user_tasks if t.completed and t.completed_at and t.completed_at.date() == day_date])

            daily_data.append({
                "date": day_date.strftime("%Y-%m-%d"),
                "day": day_str,
                "tasks_created": created_on_day,
                "tasks_completed": completed_on_day,
            })

        return {
            "has_sufficient_data": True,
            "message": "7-day productivity trend analysis",
            "daily_data": daily_data
        }


workload_service = WorkloadService()
