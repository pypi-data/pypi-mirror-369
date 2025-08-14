# rag_pipeline/chunking/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies."""
    
    @abstractmethod
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Chunk text into smaller pieces."""
        pass