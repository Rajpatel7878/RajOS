from app.llm.providers.local_provider import local_llm_provider
from app.llm.providers.openai_provider import openai_provider


class LLMRouter:

    def __init__(self):

        self.providers = {
            "local": local_llm_provider,
            "openai": openai_provider
        }


    def get_provider(
        self,
        provider_name: str = "local"
    ):

        return self.providers.get(
            provider_name,
            self.providers["local"]
        )


llm_router = LLMRouter()
