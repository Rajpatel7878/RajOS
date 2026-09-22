import re
from typing import List, Dict, Any, Tuple
from app.rag.rag_config import rag_config


class DocumentProcessor:
    """
    Normalizes document content, performs intelligent semantic chunking with overlap,
    and extracts structural metadata.
    """

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Normalizes line endings, strips whitespace, and removes repeated empty lines."""
        if not text:
            return ""
        # Replace Windows / Mac line endings
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        # Collapse >2 consecutive newlines to 2
        normalized = re.sub(r'\n{3,}', '\n\n', normalized)
        return normalized.strip()

    @classmethod
    def intelligent_chunking(
        cls,
        text: str,
        chunk_size: int = rag_config.RAG_CHUNK_SIZE,
        chunk_overlap: int = rag_config.RAG_CHUNK_OVERLAP
    ) -> List[Dict[str, Any]]:
        """
        Splits normalized text into semantically coherent chunks with overlap.
        Preserves paragraph and section boundaries where possible.
        """
        cleaned = cls.normalize_text(text)
        if not cleaned:
            return []

        # Split into natural paragraphs/sections
        paragraphs = re.split(r'\n\n+', cleaned)
        words_per_chunk = max(100, chunk_size)
        overlap_words = max(0, min(chunk_overlap, words_per_chunk // 2))

        raw_blocks = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            words = para.split()
            # If paragraph exceeds chunk_size, split paragraph by words
            if len(words) > words_per_chunk:
                for i in range(0, len(words), words_per_chunk - overlap_words):
                    sub_para = " ".join(words[i:i + words_per_chunk])
                    if sub_para:
                        raw_blocks.append(sub_para)
            else:
                raw_blocks.append(para)

        # Assemble blocks into final chunks under chunk_size limit
        chunks = []
        current_chunk_words: List[str] = []
        current_heading = "General"

        for block in raw_blocks:
            # Check if block looks like a Markdown heading
            heading_match = re.match(r'^(#{1,6}\s+.+|[A-Z0-9\s\-_]{3,}:)$', block)
            if heading_match:
                current_heading = heading_match.group(1).strip('#').strip()

            block_words = block.split()

            if len(current_chunk_words) + len(block_words) <= words_per_chunk:
                current_chunk_words.extend(block_words)
            else:
                if current_chunk_words:
                    chunk_text = " ".join(current_chunk_words)
                    chunks.append({
                        "chunk_index": len(chunks),
                        "text": chunk_text,
                        "heading": current_heading,
                        "word_count": len(current_chunk_words),
                        "char_count": len(chunk_text)
                    })

                # Retain overlap from end of current chunk
                overlap_slice = current_chunk_words[-overlap_words:] if overlap_words > 0 else []
                current_chunk_words = overlap_slice + block_words

        # Append final remaining chunk
        if current_chunk_words:
            chunk_text = " ".join(current_chunk_words)
            chunks.append({
                "chunk_index": len(chunks),
                "text": chunk_text,
                "heading": current_heading,
                "word_count": len(current_chunk_words),
                "char_count": len(chunk_text)
            })

        return chunks

    @classmethod
    def process_document_content(
        cls,
        content: str,
        filename: str = ""
    ) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Main entry point for document processing.
        Returns (success: bool, chunks: List[Dict], error_message: str).
        """
        try:
            if not content or not content.strip():
                return False, [], "Document content is empty."

            if len(content.encode('utf-8')) > rag_config.RAG_MAX_FILE_SIZE_BYTES:
                return False, [], f"Document exceeds size limit of {rag_config.RAG_MAX_FILE_SIZE_BYTES // (1024*1024)} MB."

            chunks = cls.intelligent_chunking(content)
            if not chunks:
                return False, [], "Failed to generate valid text chunks from document."

            return True, chunks, ""
        except Exception as e:
            return False, [], f"Document processing failed: {str(e)}"


document_processor = DocumentProcessor()


# Backward compatibility wrappers for legacy modules
def split_text(text: str, chunk_size: int = 500) -> List[str]:
    chunks = document_processor.intelligent_chunking(text, chunk_size=chunk_size)
    return [c["text"] for c in chunks]


def process_document(content: str) -> Dict[str, Any]:
    success, chunks, err = document_processor.process_document_content(content)
    raw_texts = [c["text"] for c in chunks]
    return {
        "total_chunks": len(raw_texts),
        "chunks": raw_texts
    }
