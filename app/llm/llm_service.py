from app.llm.llm_router import llm_router


class LLMService:


    def generate(
        self,
        prompt: str,
        provider: str = "local"
    ):

        llm_provider = llm_router.get_provider(
            provider
        )

        result = llm_provider.generate(
            prompt
        )


        if (
            provider == "openai"
            and result.get("response")
            == "OpenAI API key not configured."
        ):

            fallback = llm_router.get_provider(
                "local"
            )

            return {
                "fallback": True,
                **fallback.generate(prompt)
            }


        return result



llm_service = LLMService()
