from app.tools.base_tool import BaseTool
from app.database.connection import SessionLocal
from app.models.note import Note


class NotesTool(BaseTool):

    def name(self):
        return "notes"

    def execute(self, data):

        db = SessionLocal()

        try:
            note = Note(
                title="AI Note",
                content=data
            )

            db.add(note)
            db.commit()
            db.refresh(note)

            return {
                "tool": self.name(),
                "status": "success",
                "id": note.id,
                "title": note.title,
                "content": note.content
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
