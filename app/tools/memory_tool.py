from app.tools.base_tool import BaseTool
from app.database.connection import SessionLocal
from app.models.memory import Memory


class MemoryTool(BaseTool):

    def name(self):
        return "memory"

    def execute(self, data):

        db = SessionLocal()

        try:
            memory = Memory(
                key="user_memory",
                value=data
            )

            db.add(memory)
            db.commit()
            db.refresh(memory)

            return {
                "tool": self.name(),
                "status": "success",
                "id": memory.id,
                "key": memory.key,
                "value": memory.value
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
