import re

from app.tools.base_tool import BaseTool
from app.database.connection import SessionLocal
from app.models.note import Note


class NotesTool(BaseTool):

    def name(self):
        return "notes"

    def execute(self, data):

        db = SessionLocal()

        try:

            if isinstance(data, dict):
                message = str(data.get("message", "")).strip()
            else:
                message = str(data).strip()

            lower = message.lower()

            # Show / list notes
            if any(word in lower for word in [
                "show",
                "list",
                "display",
                "view"
            ]):

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

            # Create note
            title = None
            content = message

            # Example:
            # Create a note titled Python Functions with the content: Practice recursion.
            pattern = r"""\b(?:titled|title)\s*[:\-]?\s*["']?(.+?)["']?\s+with\s+(?:the\s+)?content\s*[:\-]?\s*(.+)"""

            match = re.search(
                pattern,
                message,
                re.IGNORECASE | re.DOTALL
            )

            if match:

                title = match.group(1).strip()
                content = match.group(2).strip()

            # Example:
            # Create a note titled Python Functions
            if not title:

                simple_pattern = r"""\b(?:titled|title)\s*[:\-]?\s*["']?(.+?)["']?$"""

                simple_match = re.search(
                    simple_pattern,
                    message,
                    re.IGNORECASE
                )

                if simple_match:
                    title = simple_match.group(1).strip()

            # Remove accidental trailing punctuation
            if title:
                title = title.rstrip(".,:;- ")

            content = re.sub(
                r"^[\s:,\-]+",
                "",
                content
            ).strip()

            if not title:
                title = "AI Note"

            note = Note(
                title=title,
                content=content
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
