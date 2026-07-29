from app.tools.base_tool import BaseTool
from app.database.connection import SessionLocal
from app.models.document import Document


class DocumentTool(BaseTool):

    def name(self):
        return "documents"

    def execute(self, data):

        db = SessionLocal()

        try:

            document = Document(
                filename=data,
                content=f"Content for {data}",
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
