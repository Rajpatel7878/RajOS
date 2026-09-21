import os
from typing import List, Dict, Any, Optional
import chromadb
from app.embeddings.embedding_service import embedding_service


class MemoryVectorStore:
    """
    ChromaDB storage wrapper for memory vector indexing and semantic retrieval.
    Enforces user_id metadata filtering on all vector queries.
    Uses ephemeral Client during pytest execution for test isolation.
    """

    def __init__(self, db_path: str = "./vector_db"):
        self.db_path = db_path
        self._init_client()

    def _init_client(self):
        if os.environ.get("TESTING") == "true" or "sqlite:///:memory:" in os.environ.get("DATABASE_URL", ""):
            self.client = chromadb.Client()
        else:
            self.client = chromadb.PersistentClient(path=self.db_path)

        self.collection = self.client.get_or_create_collection(
            name="rajOS_memories"
        )

    def add_or_update(
        self,
        memory_id: int,
        text: str,
        user_id: int,
        memory_type: str = "preference"
    ) -> bool:
        """Indexes or updates a memory embedding in ChromaDB."""
        try:
            embedding = embedding_service.generate_embedding(text)
            self.collection.upsert(
                ids=[str(memory_id)],
                documents=[text],
                embeddings=[embedding],
                metadatas=[{
                    "user_id": int(user_id),
                    "memory_id": int(memory_id),
                    "memory_type": str(memory_type)
                }]
            )
            return True
        except Exception as e:
            print(f"[MemoryVectorStore] Error indexing memory {memory_id}: {e}")
            return False

    def search(
        self,
        user_id: int,
        query_text: str,
        limit: int = 5,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Searches vector store enforcing user_id filtering."""
        try:
            count = self.collection.count()
            if count == 0:
                return []

            embedding = embedding_service.generate_embedding(query_text)
            
            if memory_type:
                where_clause = {
                    "$and": [
                        {"user_id": int(user_id)},
                        {"memory_type": str(memory_type)}
                    ]
                }
            else:
                where_clause = {"user_id": int(user_id)}

            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=min(limit, count),
                where=where_clause
            )

            hits = []
            if results and results.get("ids") and len(results["ids"]) > 0:
                ids = results["ids"][0]
                docs = results.get("documents", [[]])[0]
                metas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0] if results.get("distances") else [0.0] * len(ids)

                for i in range(len(ids)):
                    hits.append({
                        "memory_id": int(metas[i].get("memory_id", ids[i])),
                        "document": docs[i] if i < len(docs) else "",
                        "metadata": metas[i] if i < len(metas) else {},
                        "distance": distances[i] if i < len(distances) else 0.0,
                        "similarity": 1.0 / (1.0 + (distances[i] if i < len(distances) else 0.0))
                    })
            return hits
        except Exception as e:
            print(f"[MemoryVectorStore] Error searching memories for user {user_id}: {e}")
            return []

    def delete(self, memory_id: int) -> bool:
        """Removes a memory embedding from ChromaDB."""
        try:
            self.collection.delete(ids=[str(memory_id)])
            return True
        except Exception as e:
            print(f"[MemoryVectorStore] Error deleting vector memory {memory_id}: {e}")
            return False


memory_vector_store = MemoryVectorStore()
