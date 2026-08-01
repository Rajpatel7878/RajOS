from pydantic import BaseModel


class MemoryCreate(BaseModel):

    key: str
    value: str



class MemoryResponse(BaseModel):

    id: int
    key: str
    value: str

    class Config:
        from_attributes = True



class MemoryProcessRequest(BaseModel):

    message: str



class MemorySearchRequest(BaseModel):

    query: str



class MemoryStatsResponse(BaseModel):

    total_memories: int
