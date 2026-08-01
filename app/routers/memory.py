from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.memory import Memory
from app.schemas.memory_schema import (MemoryCreate, MemoryProcessRequest, MemorySearchRequest, MemoryStatsResponse)
from app.security.dependencies import get_current_user
from app.models.user import User
from app.memory.memory_engine import MemoryEngine


router = APIRouter(prefix="/memory", tags=["Memory"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_memory(
    memory: MemoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    new_memory = Memory(
        key=memory.key,
        value=memory.value,
        user_id=user.id
    )

    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)

    return new_memory


@router.get("/")
def get_memories(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    return db.query(Memory).filter(
        Memory.user_id == user.id
    ).all()


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.user_id == user.id
    ).first()

    if not memory:
        raise HTTPException(
            status_code=404,
            detail="Memory not found"
        )

    db.delete(memory)
    db.commit()

    return {
        "message": "Memory deleted"
    }


memory_engine = MemoryEngine()


@router.post("/process")
def process_memory(
    request: MemoryProcessRequest,
    user: User = Depends(get_current_user)
):

    return {
        "status": "success",
        "memories": memory_engine.process_memory(
            request.message
        )
    }



@router.post("/search")
def search_memory(
    request: MemorySearchRequest,
    user: User = Depends(get_current_user)
):

    return memory_engine.search(
        request.query
    )



@router.get("/stats", response_model=MemoryStatsResponse)
def memory_stats(
    user: User = Depends(get_current_user)
):

    return memory_engine.memory_stats()
