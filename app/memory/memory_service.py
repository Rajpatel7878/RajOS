import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.memory import Memory
from app.memory.memory_validator import memory_validator
from app.memory.memory_deduplicator import memory_deduplicator
from app.memory.memory_vector_store import memory_vector_store
from app.schemas.memory_schema import MemoryCreate, MemoryUpdate


class MemoryService:
    """
    Central service orchestrating RajOS Memory 2.0 lifecycle.
    Guarantees user data isolation, validation, deduplication, hybrid retrieval,
    explicit intent processing, and failure isolation.
    """

    def create_memory(
        self,
        db: Session,
        user_id: int,
        key: str,
        value: str,
        content: Optional[str] = None,
        memory_type: str = "preference",
        source: str = "explicit_user",
        confidence: str = "high",
        importance: str = "medium"
    ) -> Dict[str, Any]:
        """Validates, deduplicates, and creates or updates a memory."""
        # 1. Validation
        is_valid, reason = memory_validator.validate(key=key, value=value, content=content or "")
        if not is_valid:
            return {"status": "rejected", "reason": reason, "memory": None}

        # 2. Deduplication & Conflict Resolution
        action, existing_mem = memory_deduplicator.resolve_candidate(
            db=db,
            user_id=user_id,
            key=key,
            value=value,
            memory_type=memory_type
        )

        if action == "ignore" and existing_mem:
            return {"status": "ignored", "reason": "Exact or semantic duplicate already exists", "memory": existing_mem}

        if action == "update" and existing_mem:
            existing_mem.value = value
            if content:
                existing_mem.content = content
            existing_mem.memory_type = memory_type
            existing_mem.confidence = confidence
            existing_mem.importance = importance
            existing_mem.updated_at = datetime.utcnow()
            existing_mem.status = "active"
            db.commit()
            db.refresh(existing_mem)

            indexed_text = f"{existing_mem.key}: {existing_mem.value} {existing_mem.content or ''}"
            memory_vector_store.add_or_update(
                memory_id=existing_mem.id,
                text=indexed_text,
                user_id=user_id,
                memory_type=memory_type
            )
            return {"status": "updated", "reason": "Memory updated cleanly", "memory": existing_mem}

        # 3. Create new memory
        new_mem = Memory(
            user_id=user_id,
            key=key.strip(),
            value=value.strip(),
            content=content.strip() if content else None,
            memory_type=memory_type,
            source=source,
            confidence=confidence,
            importance=importance,
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            access_count=0
        )
        db.add(new_mem)
        db.commit()
        db.refresh(new_mem)

        indexed_text = f"{new_mem.key}: {new_mem.value} {new_mem.content or ''}"
        memory_vector_store.add_or_update(
            memory_id=new_mem.id,
            text=indexed_text,
            user_id=user_id,
            memory_type=memory_type
        )

        return {"status": "created", "reason": "New memory stored successfully", "memory": new_mem}

    def get_memories(
        self,
        db: Session,
        user_id: int,
        memory_type: Optional[str] = None,
        search_query: Optional[str] = None,
        status: str = "active"
    ) -> List[Memory]:
        """Gets user memories enforcing strict user_id filtering."""
        query = db.query(Memory).filter(Memory.user_id == user_id)

        if status:
            query = query.filter(Memory.status == status)

        if memory_type and memory_type.lower() != "all":
            query = query.filter(Memory.memory_type == memory_type)

        if search_query:
            term = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    Memory.key.ilike(term),
                    Memory.value.ilike(term),
                    Memory.content.ilike(term)
                )
            )

        return query.order_by(Memory.updated_at.desc()).all()

    def get_memory_by_id(self, db: Session, user_id: int, memory_id: int) -> Optional[Memory]:
        """Retrieves a single memory verifying user ownership."""
        return db.query(Memory).filter(
            Memory.id == memory_id,
            Memory.user_id == user_id
        ).first()

    def update_memory(
        self,
        db: Session,
        user_id: int,
        memory_id: int,
        update_data: MemoryUpdate
    ) -> Optional[Memory]:
        """Updates an existing memory and syncs vector store."""
        memory = self.get_memory_by_id(db, user_id, memory_id)
        if not memory:
            return None

        fields_to_update = update_data.model_dump(exclude_unset=True)
        for key, val in fields_to_update.items():
            if val is not None:
                setattr(memory, key, val)

        memory.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(memory)

        if memory.status == "active":
            indexed_text = f"{memory.key}: {memory.value} {memory.content or ''}"
            memory_vector_store.add_or_update(
                memory_id=memory.id,
                text=indexed_text,
                user_id=user_id,
                memory_type=memory.memory_type
            )
        else:
            memory_vector_store.delete(memory.id)

        return memory

    def delete_memory(self, db: Session, user_id: int, memory_id: int) -> bool:
        """Deletes a memory by setting status='deleted' and purging from vector store."""
        memory = self.get_memory_by_id(db, user_id, memory_id)
        if not memory:
            return False

        memory.status = "deleted"
        memory.updated_at = datetime.utcnow()
        db.commit()

        memory_vector_store.delete(memory_id)
        return True

    def parse_and_handle_explicit_intent(
        self,
        db: Session,
        user_id: int,
        user_message: str
    ) -> Tuple[bool, str, Optional[Memory]]:
        """
        Parses explicit memory intents from natural user messages:
        e.g., 'Remember that I prefer TypeScript for frontend code'
        'Forget my preference for dark mode'
        """
        text = user_message.strip()

        # Explicit Forget / Delete patterns
        forget_match = re.search(
            r'(?i)^(?:forget|delete memory|remove memory|don\'t remember)\s+(?:that|about|my)?\s*(.+)$',
            text
        )
        if forget_match:
            target_topic = forget_match.group(1).strip()
            memories = self.get_memories(db, user_id=user_id, status="active")
            target_lower = target_topic.lower()
            for mem in memories:
                if target_lower in mem.key.lower() or target_lower in mem.value.lower():
                    self.delete_memory(db, user_id, mem.id)
                    return True, f"Forgot memory: '{mem.key}: {mem.value}'", mem
            return True, f"No matching memory found for '{target_topic}' to forget.", None

        # Explicit Remember patterns
        remember_match = re.search(
            r'(?i)^(?:remember|don\'t forget|note that|save memory)\s+(?:that|:)?\s*(.+)$',
            text
        )
        if remember_match:
            fact = remember_match.group(1).strip()
            # Infer key, value, and memory_type
            memory_type = "preference"
            if re.search(r'(?i)\b(goal|target|aim|want to achieve)\b', fact):
                memory_type = "goal"
            elif re.search(r'(?i)\b(project|building|app|repo|working on)\b', fact):
                memory_type = "project"
            elif re.search(r'(?i)\b(always|never|must|should|format)\b', fact):
                memory_type = "instruction"
            elif re.search(r'(?i)\b(my name|i am|i live|located|work as)\b', fact):
                memory_type = "fact"

            parts = fact.split(" is ", 1) if " is " in fact else fact.split(":", 1) if ":" in fact else None
            if parts and len(parts) == 2:
                key, val = parts[0].strip(), parts[1].strip()
            else:
                key, val = "User Fact", fact

            result = self.create_memory(
                db=db,
                user_id=user_id,
                key=key,
                value=val,
                content=fact,
                memory_type=memory_type,
                source="explicit_user",
                confidence="high",
                importance="high"
            )
            mem_obj = result.get("memory")
            return True, f"Memory recorded ({result.get('status')}): {key} = {val}", mem_obj

        return False, "", None

    def extract_memories_from_conversation(
        self,
        db: Session,
        user_id: int,
        user_message: str
    ) -> List[Dict[str, Any]]:
        """
        Infers long-term memory candidates from conversation context.
        Wrapped in failure isolation so it NEVER crashes conversation flow.
        """
        extracted_results = []
        try:
            # Simple pattern-based implicit fact extraction
            implicit_patterns = [
                (r'(?i)\bmy name is ([A-Za-z0-9\s]+)\b', "User Name", "fact"),
                (r'(?i)\bi prefer ([A-Za-z0-9\s\-_]+)\b', "User Preference", "preference"),
                (r'(?i)\bi am building ([A-Za-z0-9\s\-_]+)\b', "Active Project", "project"),
                (r'(?i)\bmy goal is to ([A-Za-z0-9\s\-_]+)\b', "User Goal", "goal"),
                (r'(?i)\balways ([A-Za-z0-9\s\-_]+)\b', "System Instruction", "instruction")
            ]

            for pattern, default_key, mem_type in implicit_patterns:
                match = re.search(pattern, user_message)
                if match:
                    extracted_val = match.group(1).strip()
                    res = self.create_memory(
                        db=db,
                        user_id=user_id,
                        key=default_key,
                        value=extracted_val,
                        content=user_message,
                        memory_type=mem_type,
                        source="inferred_llm",
                        confidence="medium",
                        importance="medium"
                    )
                    extracted_results.append(res)
        except Exception as e:
            print(f"[MemoryService] Failure in implicit memory extraction (isolated): {e}")

        return extracted_results

    def get_relevant_memories_for_context(
        self,
        db: Session,
        user_id: int,
        query_text: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Hybrid vector + DB keyword retrieval for LLM prompt context injection.
        Guarantees strictly isolated user memories and updates access stats.
        """
        try:
            # 1. Vector similarity search
            vector_hits = memory_vector_store.search(
                user_id=user_id,
                query_text=query_text,
                limit=limit
            )

            matched_memory_ids = [hit["memory_id"] for hit in vector_hits if "memory_id" in hit]

            # 2. Database fetch of active memories
            memories = []
            if matched_memory_ids:
                memories = db.query(Memory).filter(
                    Memory.id.in_(matched_memory_ids),
                    Memory.user_id == user_id,
                    Memory.status == "active"
                ).all()

            # Fallback / augment with top recent memories if vector count is low
            if len(memories) < limit:
                recent_memories = db.query(Memory).filter(
                    Memory.user_id == user_id,
                    Memory.status == "active"
                ).order_by(Memory.importance.desc(), Memory.updated_at.desc()).limit(limit).all()

                existing_ids = {m.id for m in memories}
                for rm in recent_memories:
                    if rm.id not in existing_ids and len(memories) < limit:
                        memories.append(rm)

            # 3. Update access stats and format response
            formatted = []
            now = datetime.utcnow()
            for mem in memories:
                mem.last_accessed_at = now
                mem.access_count = (mem.access_count or 0) + 1
                formatted.append({
                    "id": mem.id,
                    "key": mem.key,
                    "value": mem.value,
                    "type": mem.memory_type,
                    "importance": mem.importance,
                    "content": mem.content or f"{mem.key}: {mem.value}"
                })
            db.commit()

            return formatted
        except Exception as e:
            print(f"[MemoryService] Error in context retrieval (isolated): {e}")
            return []

    def get_memory_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Calculates memory statistics for user dashboard."""
        all_memories = db.query(Memory).filter(Memory.user_id == user_id).all()
        active_memories = [m for m in all_memories if m.status == "active"]

        by_type: Dict[str, int] = {}
        by_source: Dict[str, int] = {}

        for m in active_memories:
            m_type = m.memory_type or "preference"
            m_src = m.source or "explicit_user"
            by_type[m_type] = by_type.get(m_type, 0) + 1
            by_source[m_src] = by_source.get(m_src, 0) + 1

        return {
            "total_memories": len(all_memories),
            "active_memories": len(active_memories),
            "by_type": by_type,
            "by_source": by_source
        }


memory_service = MemoryService()
