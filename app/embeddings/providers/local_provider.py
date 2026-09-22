import hashlib
import numpy as np
from typing import List


class LocalEmbeddingProvider:
    """
    Local embedding provider using SentenceTransformer with deterministic
    vector fallback when network or HF hub requests are unavailable.
    """

    def __init__(self):
        self.model = None

    def load_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                try:
                    self.model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
                except Exception:
                    self.model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                print(f"[LocalEmbeddingProvider] Notice: SentenceTransformer offline fallback active ({e})")
                self.model = False
        return self.model

    def _fallback_embedding(self, text: str, dim: int = 384) -> List[float]:
        """Generates a deterministic 384-dimensional normalized vector from text."""
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()
        for word in words:
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            val = ((h >> 8) % 1000) / 1000.0 - 0.5
            vec[idx] += val
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def create_embedding(self, text: str) -> List[float]:
        try:
            model = self.load_model()
            if model:
                return model.encode(text).tolist()
        except Exception as e:
            print(f"[LocalEmbeddingProvider] Using deterministic embedding fallback: {e}")

        return self._fallback_embedding(text)


local_provider = LocalEmbeddingProvider()
