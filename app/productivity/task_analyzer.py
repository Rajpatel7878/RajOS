from datetime import datetime

from app.database.connection import SessionLocal
from app.models.task import Task


class TaskAnalyzer:


    def analyze(self):

        db = SessionLocal()

        try:

            tasks = db.query(Task).all()

            total = len(tasks)

            completed = len([
                task for task in tasks
                if task.completed
            ])

            pending = total - completed


            completion_rate = 0

            if total > 0:
                completion_rate = round(
                    (completed / total) * 100,
                    2
                )


            priority_bonus = 0

            deadline_bonus = 0


            for task in tasks:

                if task.completed:

                    if task.priority == "high":
                        priority_bonus += 5

                    elif task.priority == "normal":
                        priority_bonus += 2


                    if task.due_date:

                        if task.completed_at and task.completed_at <= task.due_date:
                            deadline_bonus += 5


            return {
                "total_tasks": total,
                "completed_tasks": completed,
                "pending_tasks": pending,
                "completion_rate": completion_rate,
                "priority_bonus": priority_bonus,
                "deadline_bonus": deadline_bonus
            }


        finally:

            db.close()
