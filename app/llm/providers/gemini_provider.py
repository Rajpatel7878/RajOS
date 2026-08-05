from google import genai
from app.llm.providers.base_provider import BaseLLMProvider
from app.llm.llm_config import llm_config


class GeminiProvider(BaseLLMProvider):

    def __init__(self):
        self.api_key = llm_config.GEMINI_API_KEY

    def generate(self, prompt: str):

        if not self.api_key:
            return {
                "provider": "gemini",
                "response": "Gemini API key not configured."
            }

        try:
            client = genai.Client(api_key=self.api_key)

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

            return {
                "provider": "gemini",
                "response": response.text
            }

        except Exception as e:
            return {
                "provider": "gemini",
                "response": str(e)
            }


gemini_provider = GeminiProvider()
