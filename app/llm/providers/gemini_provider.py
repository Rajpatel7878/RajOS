"""Gemini LLM Provider for RajOS.

Uses the Google GenAI SDK. Model name is read from app settings
so it can be overridden via the GEMINI_MODEL environment variable
without changing source code.
"""

import logging
from google import genai
from app.llm.providers.base_provider import BaseLLMProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL  # defaults to "gemini-2.5-flash"

    def generate(self, prompt: str):

        if not self.api_key:
            logger.warning("Gemini API key not configured; skipping Gemini call.")
            return {
                "provider": "gemini",
                "response": "Gemini API key not configured."
            }

        try:
            client = genai.Client(api_key=self.api_key)

            response = client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            return {
                "provider": "gemini",
                "model": self.model,
                "response": response.text
            }

        except Exception as exc:
            logger.error("Gemini generate failed: %s", exc)
            return {
                "provider": "gemini",
                "response": f"Gemini error: {exc}"
            }


gemini_provider = GeminiProvider()
