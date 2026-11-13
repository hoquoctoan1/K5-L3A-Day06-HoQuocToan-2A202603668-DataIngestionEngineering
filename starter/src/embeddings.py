"""Pinned, local E5 embeddings with explicit document/query prefixes."""
from typing import Protocol

MODEL_NAME = "intfloat/multilingual-e5-small"
MODEL_REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"


class Embedder(Protocol):
    model_name: str
    dimensions: int
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, question: str) -> list[float]: ...


class MyEmbedder:
    dimensions = 384
    model_revision = MODEL_REVISION

    def __init__(self, model_name: str = MODEL_NAME, *, local_files_only: bool = True) -> None:
        if model_name != MODEL_NAME:
            raise ValueError("This experiment is pinned to multilingual-e5-small")
        from sentence_transformers import SentenceTransformer
        self.model_name = model_name
        self.model = SentenceTransformer(model_name, revision=self.model_revision,
                                         device="cpu", local_files_only=local_files_only)

    def _encode(self, texts):
        if not texts:
            return []
        for text in texts:
            if len(self.model.tokenizer(text, truncation=False)["input_ids"]) > self.model.max_seq_length:
                raise ValueError("Input exceeds model token limit; do not silently truncate")
        vectors = self.model.encode(texts, batch_size=16, normalize_embeddings=True)
        if vectors.shape != (len(texts), self.dimensions):
            raise ValueError("Unexpected embedding dimensions")
        return vectors.tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._encode(["passage: " + text for text in texts])

    def embed_query(self, question: str) -> list[float]:
        if not question.strip():
            raise ValueError("Question is empty")
        return self._encode(["query: " + question])[0]
