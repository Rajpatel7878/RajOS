from typing import Tuple, Optional
from sqlalchemy.orm import Session
from app.models.memory import Memory
from app.memory.memory_vector_store import memory_vector_store


class MemoryDeduplicator:
    """
    Deduplicates and resolves conflicts in memory candidates.
    Distinguishes exact duplicates, key/topic updates, and semantic overlap.
    """

    @classmethod
    def resolve_candidate(
        cls,
        db: Session,
        user_id: int,
        key: str,
        value: str,
        memory_type: str = "preference"
    ) -> Tuple[str, Optional[Memory]]:
        """
        Returns (action, existing_memory)
        action can be:
        - "ignore": exact match or semantic duplicate exists
        - "update": existing memory should be updated with new value/content
        - "create": brand new memory
        """
        normalized_key = key.strip().lower()
        normalized_value = value.strip().lower()

        # 1. Exact match search in DB for user_id
        user_memories = db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.status == "active"
        ).all()

        for mem in user_memories:
            mem_key = (mem.key or "").strip().lower()
            mem_val = (mem.value or "").strip().lower()

            # Exact key and value match
            if mem_key == normalized_key and mem_val == normalized_value:
                return "ignore", mem

            # Key match with different value -> update conflict resolution
            if mem_key == normalized_key:
                return "update", mem

        # 2. Semantic similarity search in vector store
        query_text = f"{key}: {value}"
        vector_hits = memory_vector_store.search(
            user_id=user_id,
            query_text=query_text,
            limit=3,
            memory_type=memory_type
        )

        for hit in vector_hits:
            similarity = hit.get("similarity", 0.0)
            hit_mem_id = hit.get("memory_id")
            if similarity >= 0.88 and hit_mem_id:
                existing_mem = db.query(Memory).filter(
                    Memory.id == hit_mem_id,
                    Memory.user_id == user_id,
                    Memory.status == "active"
                ).first()

                if existing_mem:
                    # If existing value is almost identical
                    if existing_mem.value.strip().lower() == normalized_value:
                        return "ignore", existing_mem
                    else:
                        return "update", existing_mem

        return "create", None


memory_deduplicator = MemoryDeduplicator()
