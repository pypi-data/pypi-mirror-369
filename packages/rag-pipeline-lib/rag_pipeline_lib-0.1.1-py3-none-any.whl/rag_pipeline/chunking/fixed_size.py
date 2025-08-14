# rag_pipeline/chunking/fixed_size.py
from typing import List, Dict, Any
from .base import ChunkingStrategy

class FixedSizeChunking(ChunkingStrategy):
    """Fixed size chunking strategy."""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Chunk text into fixed-size pieces with overlap."""
        if metadata is None:
            metadata = {}
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_index': len(chunks),
                'start_pos': start,
                'end_pos': min(end, len(text))
            })
            
            chunks.append({
                'text': chunk_text,
                'metadata': chunk_metadata
            })
            
            if end >= len(text):
                break
            
            start = end - self.overlap
        
        return chunks