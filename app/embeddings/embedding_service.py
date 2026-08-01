from app.embeddings.providers.local_provider import local_provider


class EmbeddingService:


    def __init__(self):

        self.provider = local_provider



    def generate_embedding(
        self,
        text: str
    ):

        return self.provider.create_embedding(
            text
        )



    def generate_embeddings(
        self,
        texts: list[str]
    ):

        return [
            self.generate_embedding(text)
            for text in texts
        ]



embedding_service = EmbeddingService()
