from app.tools.base_tool import BaseTool
from app.database.connection import SessionLocal
from app.models.task import Task


class TasksTool(BaseTool):

    def name(self):
        return "tasks"

    def execute(self, data):

        db = SessionLocal()

        try:
            task = Task(
                title=data,
                completed=False
            )

            db.add(task)
            db.commit()
            db.refresh(task)

            return {
                "tool": self.name(),
                "status": "success",
                "id": task.id,
                "title": task.title,
                "completed": task.completed
            }

        except Exception as e:

            db.rollback()

            return {
                "tool": self.name(),
                "status": "error",
                "message": str(e)
            }

        finally:

            db.close()
