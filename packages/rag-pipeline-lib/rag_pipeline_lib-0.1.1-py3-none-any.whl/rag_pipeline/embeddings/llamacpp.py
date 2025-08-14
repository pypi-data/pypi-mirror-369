# rag_pipeline/embeddings/llamacpp.py
from typing import List
from .base import Embedding

class LlamaCppEmbeddings  (Embedding):
    """llama.cpp HTTP server üzerinden embedding alma."""
    
    def __init__(self, model: str = "llama", base_url: str = "http://llamacpp_server:8000"):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._dimension = None

    def embed_text(self, text: str) -> List[float]:
        try:
            import requests

            payload = {
                "model": self.model,
                "prompt": text
            }

            response = requests.post(f"{self.base_url}/v1/embeddings", json=payload)
            response.raise_for_status()
            embedding = response.json()["data"][0]["embedding"]
            if self._dimension is None:
                self._dimension = len(embedding)
            return embedding

        except Exception as e:
            print(f"Embedding error: {e}")
            return []

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(text) for text in texts]

    def get_dimension(self) -> int:
        if self._dimension is None:
            sample = self.embed_text("sample")
            self._dimension = len(sample)
        return self._dimension
