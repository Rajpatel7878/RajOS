from pydantic import BaseModel


class LLMRequest(BaseModel):

    prompt: str
    provider: str = "local"



class LLMResponse(BaseModel):

    provider: str
    response: str
