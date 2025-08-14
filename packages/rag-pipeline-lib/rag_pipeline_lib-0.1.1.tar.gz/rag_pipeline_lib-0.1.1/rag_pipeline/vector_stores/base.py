# rag_pipeline/vector_stores/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
    
    @abstractmethod
    def create_collection(self, dimension: int, **kwargs) -> bool:
        """Create a new collection/index."""
        pass
    
    @abstractmethod
    def add_documents(self, texts: List[str], embeddings: List[List[float]], 
                     metadatas: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Add documents with their embeddings to the collection."""
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5, 
              similarity_threshold: float = 0.0, **kwargs) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    def delete_collection(self) -> bool:
        """Delete the collection."""
        pass