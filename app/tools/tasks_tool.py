import re

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
                message = str(data.get("message", "")).strip()
                user = data.get("user")
            else:
                message = str(data).strip()
                user = None

            if not message:
                return {
                    "tool": self.name(),
                    "status": "error",
                    "message": "Task request cannot be empty."
                }

            lower = message.lower()
            user_id = getattr(user, "id", None)

            # -------------------------
            # LIST TASKS
            # -------------------------

            if any(phrase in lower for phrase in [
                "show my tasks",
                "show tasks",
                "list my tasks",
                "list tasks",
                "my tasks",
                "what tasks do i have",
                "what are my tasks"
            ]):

                query = db.query(Task)

                if user_id is not None:
                    query = query.filter(Task.user_id == user_id)

                tasks = query.all()

                return {
                    "tool": self.name(),
                    "status": "success",
                    "operation": "list",
                    "count": len(tasks),
                    "tasks": [
                        {
                            "id": task.id,
                            "title": task.title,
                            "completed": task.completed
                        }
                        for task in tasks
                    ]
                }

            # -------------------------
            # COMPLETE TASK BY ID
            # -------------------------

            match = re.search(
                r'(?:complete|finish|done|mark\s+complete)\s+task\s+#?(\d+)',
                lower
            )

            if match:

                task_id = int(match.group(1))

                query = db.query(Task).filter(Task.id == task_id)

                if user_id is not None:
                    query = query.filter(Task.user_id == user_id)

                task = query.first()

                if not task:
                    return {
                        "tool": self.name(),
                        "status": "error",
                        "message": f"Task {task_id} was not found."
                    }

                task.completed = True

                db.commit()
                db.refresh(task)

                return {
                    "tool": self.name(),
                    "status": "success",
                    "operation": "complete",
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed
                }

            # -------------------------
            # CREATE TASK
            # -------------------------

            title = message

            patterns = [
                r'^(?:please\s+)?create\s+(?:a\s+)?task\s+(?:called|named|titled)\s*[:\-]?\s*[\'"]?(.+?)[\'"]?$',
                r'^(?:please\s+)?add\s+(?:a\s+)?task\s+(?:called|named|titled)\s*[:\-]?\s*[\'"]?(.+?)[\'"]?$',
                r'^(?:please\s+)?create\s+(?:a\s+)?task\s*[:\-]\s*[\'"]?(.+?)[\'"]?$',
                r'^(?:please\s+)?add\s+(?:a\s+)?task\s*[:\-]\s*[\'"]?(.+?)[\'"]?$',
            ]

            for pattern in patterns:

                match = re.match(
                    pattern,
                    message,
                    re.IGNORECASE
                )

                if match:
                    title = match.group(1).strip().strip('\'"')
                    break

            if not title:
                return {
                    "tool": self.name(),
                    "status": "error",
                    "message": "Task title cannot be empty."
                }

            task = Task(
                title=title,
                completed=False,
                user_id=user_id
            )

            db.add(task)
            db.commit()
            db.refresh(task)

            return {
                "tool": self.name(),
                "status": "success",
                "operation": "create",
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
