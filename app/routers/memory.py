from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.security.dependencies import get_current_user
from app.memory.memory_service import memory_service
from app.schemas.memory_schema import (
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
    ExplicitMemoryRequest,
    MemorySearchRequest,
    MemoryStatsResponse
)

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.get("/", response_model=List[MemoryResponse])
def get_memories(
    memory_type: Optional[str] = Query(None, description="Category filter: preference, goal, project, instruction, fact"),
    search: Optional[str] = Query(None, description="Search query string"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieves all active memories for the authenticated user."""
    return memory_service.get_memories(
        db=db,
        user_id=user.id,
        memory_type=memory_type,
        search_query=search,
        status="active"
    )


@router.get("/stats", response_model=MemoryStatsResponse)
def get_memory_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Gets memory counts, breakdown by type, and breakdown by source."""
    return memory_service.get_memory_stats(db=db, user_id=user.id)


@router.get("/{memory_id}", response_model=MemoryResponse)
def get_memory(
    memory_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieves a single memory by ID enforcing user isolation."""
    memory = memory_service.get_memory_by_id(db=db, user_id=user.id, memory_id=memory_id)
    if not memory or memory.status != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found"
        )
    return memory


@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(
    memory_in: MemoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Creates or updates a memory with validation and deduplication."""
    result = memory_service.create_memory(
        db=db,
        user_id=user.id,
        key=memory_in.key,
        value=memory_in.value,
        content=memory_in.content,
        memory_type=memory_in.memory_type,
        source=memory_in.source,
        confidence=memory_in.confidence,
        importance=memory_in.importance
    )

    if result.get("status") == "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("reason", "Memory candidate rejected")
        )

    mem_obj = result.get("memory")
    if not mem_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not process memory candidate"
        )
    return mem_obj


@router.put("/{memory_id}", response_model=MemoryResponse)
def update_memory(
    memory_id: int,
    memory_in: MemoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Updates an existing memory."""
    updated = memory_service.update_memory(
        db=db,
        user_id=user.id,
        memory_id=memory_id,
        update_data=memory_in
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found"
        )
    return updated


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Deletes a memory by ID."""
    success = memory_service.delete_memory(db=db, user_id=user.id, memory_id=memory_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found"
        )
    return {"status": "success", "message": "Memory deleted successfully", "id": memory_id}


@router.post("/explicit")
def process_explicit_memory(
    request: ExplicitMemoryRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Processes explicit memory intent e.g., 'Remember that I use Python' or 'Forget dark mode'."""
    handled, message, mem_obj = memory_service.parse_and_handle_explicit_intent(
        db=db,
        user_id=user.id,
        user_message=request.user_message
    )
    return {
        "handled": handled,
        "message": message,
        "memory_id": mem_obj.id if mem_obj else None
    }


@router.post("/search")
def search_memories(
    request: MemorySearchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Performs hybrid vector + keyword memory search."""
    memories = memory_service.get_relevant_memories_for_context(
        db=db,
        user_id=user.id,
        query_text=request.query,
        limit=request.limit or 5
    )
    return {"results": memories}


@router.post("/process")
def process_memory_legacy(
    request: ExplicitMemoryRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Legacy compatibility endpoint for processing text into memories."""
    handled, message, mem_obj = memory_service.parse_and_handle_explicit_intent(
        db=db,
        user_id=user.id,
        user_message=request.user_message
    )
    if not handled:
        # Fallback to extraction
        res = memory_service.extract_memories_from_conversation(
            db=db,
            user_id=user.id,
            user_message=request.user_message
        )
        return {"status": "processed", "results": res}
    return {"status": "success", "message": message, "memory_id": mem_obj.id if mem_obj else None}
