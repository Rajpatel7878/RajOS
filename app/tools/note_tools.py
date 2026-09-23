from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

from app.tools.tool_definition import ToolDefinition, ToolCategory, RiskLevel
from app.tools.tool_context import ToolExecutionContext
from app.database.connection import SessionLocal
from app.models.note import Note


class CreateNoteInput(BaseModel):
    title: str = Field(..., description="Note title", min_length=1, max_length=200)
    content: str = Field(..., description="Note content text")


class ListNotesInput(BaseModel):
    limit: Optional[int] = Field(50, description="Max number of notes to return", ge=1, le=100)


class GetNoteInput(BaseModel):
    note_id: int = Field(..., description="ID of the note to retrieve", ge=1)


class UpdateNoteInput(BaseModel):
    note_id: int = Field(..., description="ID of the note to update", ge=1)
    title: Optional[str] = Field(None, description="New title")
    content: Optional[str] = Field(None, description="New content text")


class DeleteNoteInput(BaseModel):
    note_id: int = Field(..., description="ID of the note to delete", ge=1)


class SearchNotesInput(BaseModel):
    query: str = Field(..., description="Search query string", min_length=1)
    limit: Optional[int] = Field(20, description="Max search results", ge=1, le=50)


class CreateNoteTool(ToolDefinition):
    name = "create_note"
    description = "Create a new note for the authenticated user."
    category = ToolCategory.NOTES
    read_only = False
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["notes.write"]
    args_model = CreateNoteInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = CreateNoteInput(**arguments)
        db = SessionLocal()
        try:
            note = Note(
                title=args.title,
                content=args.content,
                user_id=context.user_id
            )
            db.add(note)
            db.commit()
            db.refresh(note)
            return {
                "note_id": note.id,
                "title": note.title,
                "created_at": note.created_at.isoformat() if note.created_at else None
            }
        finally:
            db.close()


class ListNotesTool(ToolDefinition):
    name = "list_notes"
    description = "List all notes belonging to the authenticated user."
    category = ToolCategory.NOTES
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["notes.read"]
    args_model = ListNotesInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = ListNotesInput(**arguments)
        db = SessionLocal()
        try:
            notes = db.query(Note).filter(Note.user_id == context.user_id).order_by(Note.id.desc()).limit(args.limit).all()
            return {
                "count": len(notes),
                "notes": [
                    {
                        "id": n.id,
                        "title": n.title,
                        "content_snippet": n.content[:150] if n.content else "",
                        "created_at": n.created_at.isoformat() if n.created_at else None
                    }
                    for n in notes
                ]
            }
        finally:
            db.close()


class GetNoteTool(ToolDefinition):
    name = "get_note"
    description = "Retrieve full note content by ID."
    category = ToolCategory.NOTES
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["notes.read"]
    args_model = GetNoteInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = GetNoteInput(**arguments)
        db = SessionLocal()
        try:
            note = db.query(Note).filter(Note.id == args.note_id, Note.user_id == context.user_id).first()
            if not note:
                raise ValueError(f"Note with ID {args.note_id} was not found.")
            return {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at.isoformat() if note.created_at else None
            }
        finally:
            db.close()


class UpdateNoteTool(ToolDefinition):
    name = "update_note"
    description = "Update an existing note's title or content."
    category = ToolCategory.NOTES
    read_only = False
    risk_level = RiskLevel.MEDIUM
    requires_confirmation = False
    required_permissions = ["notes.write"]
    args_model = UpdateNoteInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = UpdateNoteInput(**arguments)
        db = SessionLocal()
        try:
            note = db.query(Note).filter(Note.id == args.note_id, Note.user_id == context.user_id).first()
            if not note:
                raise ValueError(f"Note with ID {args.note_id} was not found.")
            if args.title is not None:
                note.title = args.title
            if args.content is not None:
                note.content = args.content
            db.commit()
            db.refresh(note)
            return {
                "id": note.id,
                "title": note.title,
                "updated_at": note.updated_at.isoformat() if hasattr(note, 'updated_at') and note.updated_at else None
            }
        finally:
            db.close()


class DeleteNoteTool(ToolDefinition):
    name = "delete_note"
    description = "Delete a note by ID. Requires user confirmation."
    category = ToolCategory.NOTES
    read_only = False
    risk_level = RiskLevel.HIGH
    requires_confirmation = True
    required_permissions = ["notes.write"]
    args_model = DeleteNoteInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = DeleteNoteInput(**arguments)
        db = SessionLocal()
        try:
            note = db.query(Note).filter(Note.id == args.note_id, Note.user_id == context.user_id).first()
            if not note:
                raise ValueError(f"Note with ID {args.note_id} was not found.")
            deleted_title = note.title
            db.delete(note)
            db.commit()
            return {
                "note_id": args.note_id,
                "deleted_title": deleted_title,
                "status": "deleted"
            }
        finally:
            db.close()


class SearchNotesTool(ToolDefinition):
    name = "search_notes"
    description = "Search notes by title or content matching the query keyword."
    category = ToolCategory.NOTES
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["notes.read"]
    args_model = SearchNotesInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = SearchNotesInput(**arguments)
        db = SessionLocal()
        try:
            search_pattern = f"%{args.query}%"
            notes = db.query(Note).filter(
                Note.user_id == context.user_id,
                (Note.title.ilike(search_pattern)) | (Note.content.ilike(search_pattern))
            ).limit(args.limit).all()
            return {
                "query": args.query,
                "count": len(notes),
                "notes": [
                    {
                        "id": n.id,
                        "title": n.title,
                        "snippet": n.content[:200] if n.content else ""
                    }
                    for n in notes
                ]
            }
        finally:
            db.close()
