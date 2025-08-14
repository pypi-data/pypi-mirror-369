# rag_pipeline/embeddings/ollama.py
from typing import List
from .base import Embedding

class OllamaEmbeddings(Embedding):
    """Ollama embeddings implementation."""
    
    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self._dimension = None
    
    def embed_text(self, text: str) -> List[float]:
        """Embed single text using Ollama."""
        try:
            import requests
            
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text}
            )
            response.raise_for_status()
            
            embedding = response.json()["embedding"]
            if self._dimension is None:
                self._dimension = len(embedding)
            
            return embedding
        except Exception as e:
            print(f"Error getting embedding from Ollama: {e}")
            return []
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts using Ollama."""
        return [self.embed_text(text) for text in texts]
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        if self._dimension is None:
            # Get dimension by embedding a sample text
            sample_embedding = self.embed_text("sample")
            if not sample_embedding:
                raise RuntimeError("Could not determine embedding dimension from Ollama.")
            self._dimension = len(sample_embedding)
        return self._dimension