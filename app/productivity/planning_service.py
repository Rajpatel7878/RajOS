from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.task import Task
from app.productivity.priority_engine import priority_engine


class PlanningService:
    """
    Day planning and Task Breakdown Service.
    Generates actionable recommendations without mutating database state.
    """

    def plan_day(
        self,
        db: Session,
        user_id: int,
        available_minutes: Optional[int] = None,
        constraints: Optional[str] = None
    ) -> Dict[str, Any]:
        pending_tasks = db.query(Task).filter(Task.user_id == user_id, Task.completed == False).all()

        if not pending_tasks:
            return {
                "message": "No pending tasks found. Your schedule is clear!",
                "allocated_minutes": 0,
                "available_minutes": available_minutes,
                "schedule": []
            }

        # Score and sort pending tasks
        scored_tasks = []
        for t in pending_tasks:
            sub_count = db.query(Task).filter(Task.parent_task_id == t.id).count()
            p_res = priority_engine.analyze_priority(t, subtasks_count=sub_count)
            est_mins = t.estimated_duration or 45  # Default 45m estimate if unspecified

            scored_tasks.append({
                "task_id": t.id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "computed_priority": p_res["computed_priority"],
                "score": p_res["priority_score"],
                "estimated_minutes": est_mins,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "reasons": p_res["reasons"]
            })

        scored_tasks.sort(key=lambda x: x["score"], reverse=True)

        schedule = []
        allocated = 0
        max_minutes = available_minutes if available_minutes and available_minutes > 0 else 480  # Default 8 hours

        for item in scored_tasks:
            if allocated + item["estimated_minutes"] <= max_minutes:
                schedule.append(item)
                allocated += item["estimated_minutes"]
            elif len(schedule) == 0:
                # Always include at least one task even if it exceeds available time
                schedule.append(item)
                allocated += item["estimated_minutes"]
                break

        return {
            "summary": f"Planned {len(schedule)} task(s) totaling {allocated} minutes ({allocated // 60}h {allocated % 60}m).",
            "available_minutes": available_minutes or 480,
            "allocated_minutes": allocated,
            "schedule": schedule,
            "unassigned_tasks_count": len(scored_tasks) - len(schedule)
        }

    def breakdown_task(
        self,
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Suggests logical subtask breakdown for a complex task.
        Returns proposed subtasks. Does NOT automatically write to DB.
        """
        # Rule-based / LLM fallback structure for breakdown
        title_lower = title.lower()
        subtasks = []

        if "project" in title_lower or "build" in title_lower or "app" in title_lower:
            subtasks = [
                {"title": f"Define requirements for '{title}'", "estimated_duration": 30, "category": "Planning"},
                {"title": f"Design architecture & data schema", "estimated_duration": 45, "category": "Design"},
                {"title": f"Implement core functionality", "estimated_duration": 90, "category": "Development"},
                {"title": f"Test & fix bugs", "estimated_duration": 45, "category": "Testing"},
                {"title": f"Final documentation & review", "estimated_duration": 30, "category": "Docs"}
            ]
        elif "assignment" in title_lower or "study" in title_lower or "paper" in title_lower or "report" in title_lower:
            subtasks = [
                {"title": f"Gather research & lecture material for '{title}'", "estimated_duration": 30, "category": "Research"},
                {"title": "Outline key sections & main arguments", "estimated_duration": 25, "category": "Outline"},
                {"title": "Draft initial content", "estimated_duration": 60, "category": "Writing"},
                {"title": "Review, edit, and format submission", "estimated_duration": 30, "category": "Review"}
            ]
        else:
            subtasks = [
                {"title": f"Prepare requirements & resources for '{title}'", "estimated_duration": 20, "category": "Preparation"},
                {"title": f"Execute main steps for '{title}'", "estimated_duration": 45, "category": "Execution"},
                {"title": f"Review output and finalize", "estimated_duration": 15, "category": "Completion"}
            ]

        total_est = sum(s["estimated_duration"] for s in subtasks)

        return {
            "parent_task_title": title,
            "suggested_subtasks": subtasks,
            "total_subtasks": len(subtasks),
            "total_estimated_duration": total_est,
            "note": "These are proposed subtasks. Confirm to create them using create_task tool."
        }


planning_service = PlanningService()
