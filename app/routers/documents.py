from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.security.dependencies import get_current_user
from app.rag.knowledge_service import knowledge_service
from app.schemas.document_schema import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    SearchRequest,
    SearchResponse,
    KnowledgeStatsResponse
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: ready, processing, failed"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Lists all knowledge documents owned by the authenticated user."""
    return knowledge_service.get_documents(db=db, user_id=user.id, status=status_filter)


@router.get("/stats", response_model=KnowledgeStatsResponse)
def get_knowledge_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieves knowledge base statistics for authenticated user."""
    return knowledge_service.get_knowledge_stats(db=db, user_id=user.id)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieves a single document by ID with security scoping."""
    doc = knowledge_service.get_document_by_id(db=db, user_id=user.id, document_id=document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return doc


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    doc_in: DocumentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Uploads, processes, chunks, embeds, and indexes a new document."""
    res = knowledge_service.ingest_document(
        db=db,
        user_id=user.id,
        filename=doc_in.filename,
        content=doc_in.content,
        title=doc_in.title,
        mime_type=doc_in.mime_type or "text/plain"
    )

    document = res.get("document")
    if not document:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=res.get("error", "Failed to process document")
        )
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    doc_in: DocumentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Updates an existing document and re-indexes vector chunks if content changed."""
    updated = knowledge_service.update_document(
        db=db,
        user_id=user.id,
        document_id=document_id,
        filename=doc_in.filename,
        title=doc_in.title,
        content=doc_in.content
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return updated


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Deletes a document and purges all associated vector chunks from ChromaDB."""
    success = knowledge_service.delete_document(db=db, user_id=user.id, document_id=document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return {"status": "success", "message": "Document and associated vectors deleted successfully", "id": document_id}


@router.post("/search", response_model=SearchResponse)
def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Performs hybrid vector + keyword knowledge search with relevance thresholding."""
    hits = knowledge_service.search_knowledge(
        db=db,
        user_id=user.id,
        query_text=request.query,
        limit=request.limit or 5
    )

    results = []
    for hit in hits:
        results.append({
            "chunk_id": str(hit.get("chunk_id", "")),
            "document_id": int(hit.get("document_id", 0)),
            "filename": str(hit.get("filename", "")),
            "heading": str(hit.get("heading", "General")),
            "content": str(hit.get("content", "")),
            "score": round(float(hit.get("score", 0.0)), 4)
        })

    return {
        "query": request.query,
        "results": results
    }
