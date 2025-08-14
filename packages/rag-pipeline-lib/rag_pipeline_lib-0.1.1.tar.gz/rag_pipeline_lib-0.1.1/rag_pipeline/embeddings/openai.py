from typing import List
from .base import Embedding
from openai import OpenAI
import os

class OpenAIEmbedding(Embedding):
    """OpenAI embeddings implementation."""
    def __init__(self, model: str = "text-embedding-ada-002"):
        self.model = model
        self._dimension = 1536  # sabit, ama API'den de öğrenebilirsin
        
        # Environment variable'dan API anahtarını al
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        
        self.client = OpenAI(api_key=api_key)
    
    def embed_text(self, text: str) -> List[float]:
        """Embed single text using OpenAI."""
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts using OpenAI."""
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [d.embedding for d in response.data]
    
    def get_dimension(self) -> int:
        return self._dimension