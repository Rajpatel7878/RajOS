from sentence_transformers import SentenceTransformer


class LocalEmbeddingProvider:

    def __init__(self):

        self.model = None


    def load_model(self):

        if self.model is None:

            self.model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

        return self.model


    def create_embedding(
        self,
        text: str
    ):

        model = self.load_model()

        return model.encode(
            text
        ).tolist()


local_provider = LocalEmbeddingProvider()
