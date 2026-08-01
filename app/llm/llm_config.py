import os


class LLMConfig:

    DEFAULT_PROVIDER = os.getenv(
        "DEFAULT_LLM_PROVIDER",
        "local"
    )


    OPENAI_API_KEY = os.getenv(
        "OPENAI_API_KEY",
        None
    )


llm_config = LLMConfig()
