from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.models.task import Task


class PriorityEngine:
    """
    Deterministic priority scoring and analysis service.
    
    Formula:
    Score = User Priority Base + Deadline Urgency + Dependency Impact + Age Score + Quick Win Bonus - Heavy Penalty
    
    Returns explainable reasons without overwriting user-defined priority.
    """

    def analyze_priority(self, task: Task, subtasks_count: int = 0) -> Dict[str, Any]:
        user_priority = (task.priority or "normal").lower()
        now = datetime.utcnow()
        reasons: List[str] = []

        # 1. Base user priority score
        if user_priority == "high":
            base_score = 40
            reasons.append("Marked high priority by user (+40)")
        elif user_priority == "normal":
            base_score = 20
            reasons.append("User priority normal (+20)")
        else:  # low
            base_score = 10
            reasons.append("User priority low (+10)")

        # 2. Deadline Urgency
        urgency_score = 0
        is_overdue = False
        is_due_today = False
        is_due_soon = False

        if task.due_date:
            days_remaining = (task.due_date - now).total_seconds() / 86400.0
            if days_remaining < 0:
                is_overdue = True
                urgency_score = 50
                reasons.append(f"Overdue by {abs(int(days_remaining))} day(s) (+50)")
            elif days_remaining <= 1.0:
                is_due_today = True
                urgency_score = 35
                reasons.append("Due today (+35)")
            elif days_remaining <= 3.0:
                is_due_soon = True
                urgency_score = 20
                reasons.append(f"Due within 3 days ({round(days_remaining, 1)} days left) (+20)")
            elif days_remaining <= 7.0:
                urgency_score = 10
                reasons.append("Due this week (+10)")

        # 3. Dependency Impact (blocking subtasks)
        dependency_score = 0
        if subtasks_count > 0:
            dependency_score = min(subtasks_count * 10, 30)
            reasons.append(f"Blocks {subtasks_count} subtask(s) (+{dependency_score})")

        # 4. Task Age (pending time)
        age_score = 0
        if task.created_at and not task.completed:
            age_days = (now - task.created_at).days
            if age_days > 0:
                age_score = min(age_days * 2, 15)
                reasons.append(f"Pending for {age_days} day(s) (+{age_score})")

        # 5. Effort Adjustment (Quick win vs Heavy task)
        effort_score = 0
        est_duration = task.estimated_duration or 0
        if 0 < est_duration <= 30:
            effort_score = 10
            reasons.append("Quick win (<= 30 mins) (+10)")
        elif est_duration >= 120:
            effort_score = -5
            reasons.append("Heavy effort task (>= 2 hours) (-5)")

        total_score = min(base_score + urgency_score + dependency_score + age_score + effort_score, 100)

        # Categorize computed priority
        if total_score >= 80:
            computed_priority = "urgent"
        elif total_score >= 55:
            computed_priority = "high"
        elif total_score >= 30:
            computed_priority = "normal"
        else:
            computed_priority = "low"

        return {
            "task_id": task.id,
            "title": task.title,
            "user_priority": user_priority,
            "computed_priority": computed_priority,
            "priority_score": total_score,
            "is_overdue": is_overdue,
            "is_due_today": is_due_today,
            "is_due_soon": is_due_soon,
            "reasons": reasons
        }


priority_engine = PriorityEngine()
