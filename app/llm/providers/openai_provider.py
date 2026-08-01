from app.llm.providers.base_provider import BaseLLMProvider
from app.llm.llm_config import llm_config


class OpenAIProvider(BaseLLMProvider):

    def __init__(self):

        self.api_key = llm_config.OPENAI_API_KEY


    def generate(
        self,
        prompt: str
    ):

        if not self.api_key:

            return {
                "provider": "openai",
                "response": "OpenAI API key not configured."
            }


        return {
            "provider": "openai",
            "response": f"OpenAI response for: {prompt}"
        }


openai_provider = OpenAIProvider()
