from pydantic import BaseModel


class KnowledgeAddRequest(BaseModel):

    doc_id: str
    content: str



class RAGQueryRequest(BaseModel):

    question: str
