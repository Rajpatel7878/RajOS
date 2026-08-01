from pydantic import BaseModel


class DocumentCreate(BaseModel):
    filename: str
    content: str


class DocumentUpdate(BaseModel):
    filename: str | None = None
    content: str | None = None


class SearchRequest(BaseModel):
    query: str


class DocumentResponse(BaseModel):
    id: int
    filename: str
    content: str
    user_id: int

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
