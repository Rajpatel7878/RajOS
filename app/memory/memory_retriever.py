from app.database.connection import SessionLocal
from app.models.memory import Memory


class MemoryRetriever:

    def get_all(self):

        db = SessionLocal()

        try:

            memories = db.query(Memory).all()

            return [
                {
                    "id": memory.id,
                    "key": memory.key,
                    "value": memory.value
                }
                for memory in memories
            ]

        finally:

            db.close()
