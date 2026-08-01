from pydantic import BaseModel
from typing import List, Any
from typing import Literal


class SearchRequest(BaseModel):
    query: str
    page: int = 1
    limit: int = 10
    type: Literal[
        "all",
        "tasks",
        "notes",
        "memories",
        "conversations",
        "documents",
    ] = "all"


class SearchResult(BaseModel):
    tasks: List[Any] = []
    notes: List[Any] = []
    memories: List[Any] = []
    conversations: List[Any] = []
    documents: List[Any] = []

    total_results: int = 0
    page: int = 1
    limit: int = 10
