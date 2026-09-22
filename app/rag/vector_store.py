import os
from typing import List, Dict, Any, Optional
import chromadb
from app.embeddings.embedding_service import embedding_service


class KnowledgeVectorStore:
    """
    ChromaDB vector store for knowledge base document chunks.
    Enforces user_id metadata filtering on all queries and operations.
    Uses ephemeral memory client during test execution for test isolation.
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
            name="rajOS_knowledge"
        )

    def add_or_update_chunks(
        self,
        user_id: int,
        document_id: int,
        filename: str,
        chunks: List[Dict[str, Any]]
    ) -> bool:
        """Indexes or updates document chunks in ChromaDB."""
        if not chunks:
            return True

        try:
            ids = []
            documents = []
            embeddings = []
            metadatas = []

            texts = [chunk["text"] for chunk in chunks]
            vectors = embedding_service.generate_embeddings(texts)

            for i, chunk in enumerate(chunks):
                chunk_id = f"doc_{document_id}_chunk_{chunk.get('chunk_index', i)}"
                ids.append(chunk_id)
                documents.append(chunk["text"])
                embeddings.append(vectors[i])
                metadatas.append({
                    "user_id": int(user_id),
                    "document_id": int(document_id),
                    "chunk_id": chunk_id,
                    "chunk_index": int(chunk.get("chunk_index", i)),
                    "filename": str(filename),
                    "heading": str(chunk.get("heading", "General"))
                })

            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            print(f"[KnowledgeVectorStore] Error indexing chunks for doc {document_id}: {e}")
            return False

    def search(
        self,
        user_id: int,
        query_text: str,
        limit: int = 5,
        document_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Performs vector similarity search enforcing user_id scoping."""
        try:
            count = self.collection.count()
            if count == 0:
                return []

            query_vector = embedding_service.generate_embedding(query_text)

            if document_id:
                where_clause = {
                    "$and": [
                        {"user_id": int(user_id)},
                        {"document_id": int(document_id)}
                    ]
                }
            else:
                where_clause = {"user_id": int(user_id)}

            results = self.collection.query(
                query_embeddings=[query_vector],
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
                    dist = distances[i] if i < len(distances) else 0.0
                    similarity = 1.0 / (1.0 + dist)
                    hits.append({
                        "chunk_id": ids[i],
                        "document_id": int(metas[i].get("document_id", 0)),
                        "chunk_index": int(metas[i].get("chunk_index", 0)),
                        "filename": metas[i].get("filename", ""),
                        "heading": metas[i].get("heading", "General"),
                        "content": docs[i] if i < len(docs) else "",
                        "metadata": metas[i] if i < len(metas) else {},
                        "distance": dist,
                        "similarity": similarity
                    })
            return hits
        except Exception as e:
            print(f"[KnowledgeVectorStore] Error searching vectors for user {user_id}: {e}")
            return []

    def delete_document_chunks(self, user_id: int, document_id: int) -> bool:
        """Deletes all vector chunks belonging to document_id for user_id."""
        try:
            self.collection.delete(
                where={
                    "$and": [
                        {"user_id": int(user_id)},
                        {"document_id": int(document_id)}
                    ]
                }
            )
            return True
        except Exception as e:
            print(f"[KnowledgeVectorStore] Error deleting vector chunks for doc {document_id}: {e}")
            return False


knowledge_vector_store = KnowledgeVectorStore()


# Backward compatibility wrappers for legacy modules
def add_document(doc_id: str, text: str, embedding: list):
    try:
        knowledge_vector_store.collection.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding]
        )
    except Exception as e:
        print(f"[vector_store] Legacy add_document error: {e}")


def search_document(embedding: list):
    try:
        return knowledge_vector_store.collection.query(
            query_embeddings=[embedding],
            n_results=3
        )
    except Exception as e:
        print(f"[vector_store] Legacy search_document error: {e}")
        return {}
