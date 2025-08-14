# rag_pipeline/embeddings/huggingface.py
from typing import List
from .base import Embedding

class HuggingFaceEmbeddings(Embedding):
    """HuggingFace embeddings implementation."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load HuggingFace model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except ImportError:
            raise ImportError("sentence-transformers is required for HuggingFaceEmbeddings")
    
    def embed_text(self, text: str) -> List[float]:
        """Embed single text using HuggingFace."""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts using HuggingFace."""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()