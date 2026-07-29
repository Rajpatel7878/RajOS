from app.database.connection import SessionLocal
from app.models.memory import Memory


class MemoryStore:

    def save(self, key, value):

        db = SessionLocal()

        try:
            memory = Memory(
                key=key,
                value=value
            )

            db.add(memory)
            db.commit()
            db.refresh(memory)

            return {
                "status": "success",
                "id": memory.id,
                "key": memory.key,
                "value": memory.value
            }

        except Exception as e:

            db.rollback()

            return {
                "status": "error",
                "message": str(e)
            }

        finally:

            db.close()
