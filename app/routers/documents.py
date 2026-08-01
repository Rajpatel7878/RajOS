from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.document import Document
from app.schemas.document_schema import DocumentCreate
from app.models.user import User
from app.security.dependencies import get_current_user

from app.rag.document_processor import process_document
from app.rag.embeddings import create_embedding
from app.rag.vector_store import add_document


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def upload_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    new_document = Document(
        filename=document.filename,
        content=document.content,
        user_id=user.id
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)


    processed = process_document(
        document.content
    )


    for index, chunk in enumerate(
        processed["chunks"]
    ):

        embedding = create_embedding(
            chunk
        )

        add_document(
            doc_id=f"{new_document.id}_{index}",
            text=chunk,
            embedding=embedding
        )


    return {
        "message": "Document processed successfully",
        "document_id": new_document.id,
        "chunks": processed["total_chunks"]
    }


@router.get("/")
def get_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    return db.query(Document).filter(
        Document.user_id == user.id
    ).all()


from app.schemas.document_schema import SearchRequest
from app.rag.vector_store import search_document


@router.post("/search")
def search_documents(
    request: SearchRequest,
    user: User = Depends(get_current_user)
):

    query_embedding = create_embedding(
        request.query
    )

    results = search_document(
        query_embedding
    )

    return {
        "results": results
    }

from fastapi import HTTPException
from app.schemas.document_schema import DocumentUpdate


@router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


@router.put("/{document_id}")
def update_document(
    document_id: int,
    request: DocumentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    if request.filename is not None:
        document.filename = request.filename

    if request.content is not None:
        document.content = request.content

    db.commit()
    db.refresh(document)

    return {
        "message": "Document updated successfully",
        "document": document
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully"
    }
