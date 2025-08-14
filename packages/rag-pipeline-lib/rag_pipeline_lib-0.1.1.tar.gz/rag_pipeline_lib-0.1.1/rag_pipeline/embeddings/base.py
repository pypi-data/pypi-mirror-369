# rag_pipeline/embeddings/base.py
from abc import ABC, abstractmethod
from typing import List

class Embedding(ABC):
    """Abstract base class for embeddings."""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text."""
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        pass