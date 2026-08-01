from app.tools.base_tool import BaseTool
from app.database.connection import SessionLocal
from app.models.task import Task


class TasksTool(BaseTool):

    def name(self):
        return "tasks"

    def execute(self, data):

        db = SessionLocal()

        try:

            if isinstance(data, dict):
                title = data.get("message", "").strip()
                user = data.get("user")
            else:
                title = str(data).strip()
                user = None

            if not title:
                return {
                    "tool": self.name(),
                    "status": "error",
                    "message": "Task title cannot be empty."
                }

            task = Task(
                title=title,
                completed=False,
                user_id=getattr(user, "id", None)
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
