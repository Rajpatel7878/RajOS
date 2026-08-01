from app.llm.providers.base_provider import BaseLLMProvider


class LocalLLMProvider(BaseLLMProvider):

    def generate(
        self,
        prompt: str
    ):

        return {
            "provider": "local",
            "response": f"Local LLM response for: {prompt}"
        }


local_llm_provider = LocalLLMProvider()
