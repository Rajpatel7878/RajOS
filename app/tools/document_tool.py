from app.tools.base_tool import BaseTool
from app.database.connection import SessionLocal
from app.models.document import Document


class DocumentTool(BaseTool):

    def name(self):
        return "documents"

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

                documents = db.query(Document).all()

                return {
                    "tool": self.name(),
                    "status": "success",
                    "count": len(documents),
                    "documents": [
                        {
                            "id": doc.id,
                            "filename": doc.filename
                        }
                        for doc in documents
                    ]
                }

            if "search" in lower:

                keyword = (
                    lower.replace("search", "")
                    .replace("document", "")
                    .replace("documents", "")
                    .strip()
                )

                documents = db.query(Document).filter(
                    Document.filename.ilike(f"%{keyword}%")
                ).all()

                return {
                    "tool": self.name(),
                    "status": "success",
                    "count": len(documents),
                    "documents": [
                        {
                            "id": doc.id,
                            "filename": doc.filename
                        }
                        for doc in documents
                    ]
                }

            document = Document(
                filename=message,
                content=f"Content for {message}",
                user_id=None
            )

            db.add(document)
            db.commit()
            db.refresh(document)

            return {
                "tool": self.name(),
                "status": "success",
                "id": document.id,
                "filename": document.filename,
                "content": document.content
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
