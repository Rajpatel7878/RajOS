from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.note import Note
from app.schemas.note_schema import NoteCreate
from app.security.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/notes", tags=["Notes"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    new_note = Note(
        title=note.title,
        content=note.content,
        user_id=user.id
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


@router.get("/")
def get_notes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    return db.query(Note).filter(
        Note.user_id == user.id
    ).all()


@router.get("/{note_id}")
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user.id
    ).first()

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return note


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user.id
    ).first()

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    db.delete(note)
    db.commit()

    return {
        "message": "Note deleted"
    }
