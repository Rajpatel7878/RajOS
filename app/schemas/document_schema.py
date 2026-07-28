from pydantic import BaseModel


class DocumentCreate(BaseModel):
    filename: str
    content: str


class SearchRequest(BaseModel):
    query: str


class DocumentResponse(BaseModel):
    id: int
    filename: str
    content: str

    class Config:
        from_attributes = True
