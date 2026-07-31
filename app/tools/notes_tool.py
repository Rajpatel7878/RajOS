from app.tools.base_tool import BaseTool
from app.database.connection import SessionLocal
from app.models.note import Note


class NotesTool(BaseTool):

    def name(self):
        return "notes"

    def execute(self, data):

        db = SessionLocal()

        try:

            message = ""

            if isinstance(data, dict):
                message = data.get("message", "")
            else:
                message = str(data)

            lower = message.lower()

            if "show" in lower or "list" in lower:

                notes = db.query(Note).all()

                return {
                    "tool": self.name(),
                    "status": "success",
                    "count": len(notes),
                    "notes": [
                        {
                            "id": note.id,
                            "title": note.title,
                            "content": note.content
                        }
                        for note in notes
                    ]
                }

            note = Note(
                title="AI Note",
                content=message
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
