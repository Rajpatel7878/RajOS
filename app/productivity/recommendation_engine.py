import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.task import Task
from app.productivity.task_analyzer import task_analyzer
from app.productivity.priority_engine import priority_engine


class RecommendationEngine:
    """
    Generate explainable, structured, non-destructive recommendations.
    Never modifies database records automatically.
    """

    def generate_recommendations(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        analysis = task_analyzer.analyze_user_tasks(db, user_id)
        recommendations: List[Dict[str, Any]] = []

        # 1. Overdue Tasks Recommendation
        if analysis["overdue_tasks"]:
            top_overdue = sorted(analysis["overdue_tasks"], key=lambda x: x["priority_score"], reverse=True)[0]
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "overdue_task",
                "title": f"Resolve overdue task: '{top_overdue['title']}'",
                "description": f"This task was due on {top_overdue['due_date']} and remains incomplete.",
                "reason": f"Overdue task with priority score {top_overdue['priority_score']}. Overdue work creates backlog pressure.",
                "related_task_ids": [top_overdue["id"]],
                "action_suggestion": "Complete task or reschedule due date",
                "priority": "urgent"
            })

        # 2. Deadline Risk Recommendation (due within 3 days)
        if analysis["due_soon_tasks"]:
            top_due_soon = analysis["due_soon_tasks"][0]
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "deadline_risk",
                "title": f"Upcoming deadline: '{top_due_soon['title']}'",
                "description": f"Due on {top_due_soon['due_date']}.",
                "reason": f"Approaching deadline within 3 days. Estimated duration: {top_due_soon['estimated_duration'] or 'Not set'} mins.",
                "related_task_ids": [top_due_soon["id"]],
                "action_suggestion": "Block time on schedule today",
                "priority": "high"
            })

        # 3. Quick Win Recommendation
        if analysis["quick_wins"]:
            qw = analysis["quick_wins"][0]
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "quick_win",
                "title": f"Quick win candidate: '{qw['title']}'",
                "description": "Short task that can be completed in <30 minutes.",
                "reason": "Completing quick wins builds momentum and reduces total pending task count.",
                "related_task_ids": [qw["id"]],
                "action_suggestion": "Complete now (approx. 15-30 mins)",
                "priority": "normal"
            })

        # 4. Unscheduled Important Task
        if analysis["unscheduled_tasks"]:
            un_task = analysis["unscheduled_tasks"][0]
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "missing_deadline",
                "title": f"Set due date for high-priority task: '{un_task['title']}'",
                "description": "High priority task currently lacks a deadline.",
                "reason": "High priority tasks without deadlines run the risk of becoming stale or forgotten.",
                "related_task_ids": [un_task["id"]],
                "action_suggestion": "Assign a target due date",
                "priority": "normal"
            })

        # 5. Heavy Task Breakdown Recommendation
        if analysis["heavy_tasks"]:
            heavy = analysis["heavy_tasks"][0]
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "task_breakdown",
                "title": f"Break down large task: '{heavy['title']}'",
                "description": f"Estimated at {heavy['estimated_duration']} minutes.",
                "reason": "Large tasks (>= 2 hours) are easier to execute when divided into smaller actionable subtasks.",
                "related_task_ids": [heavy["id"]],
                "action_suggestion": "Ask RajOS AI to generate a subtask breakdown",
                "priority": "normal"
            })

        # Default recommendation if no tasks exist
        if not recommendations and analysis["total_tasks"] == 0:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "type": "planning",
                "title": "Welcome to RajOS Productivity Intelligence",
                "description": "You currently have 0 tasks stored.",
                "reason": "Create your first task to unlock automated workload analysis and AI recommendations.",
                "related_task_ids": [],
                "action_suggestion": "Create a task using the + Add Task button or AI Assistant",
                "priority": "low"
            })

        return recommendations


recommendation_engine = RecommendationEngine()
