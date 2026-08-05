import os
from dotenv import load_dotenv

load_dotenv()


class LLMConfig:

    DEFAULT_PROVIDER = os.getenv(
        "DEFAULT_LLM_PROVIDER",
        "local"
    )

    OPENAI_API_KEY = os.getenv(
        "OPENAI_API_KEY"
    )

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY"
    )


llm_config = LLMConfig()
