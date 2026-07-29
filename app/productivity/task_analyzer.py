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


            return {
                "total_tasks": total,
                "completed_tasks": completed,
                "pending_tasks": pending,
                "completion_rate": completion_rate
            }


        finally:

            db.close()
