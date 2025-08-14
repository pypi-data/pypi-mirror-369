# rag_pipeline/chunking/semantic.py
import re
from typing import List, Dict, Any
from .base import ChunkingStrategy

class SemanticChunking(ChunkingStrategy):
    """Semantic chunking strategy based on sentences/paragraphs."""
    
    def __init__(self, max_chunk_size: int = 512, min_chunk_size: int = 100):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Chunk text based on semantic boundaries (sentences/paragraphs)."""
        if metadata is None:
            metadata = {}
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # Use a more robust sentence splitter
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # Check if adding this sentence would exceed max size
                if len(current_chunk) + len(sentence) + 1 > self.max_chunk_size and len(current_chunk) > self.min_chunk_size:
                    chunk_metadata = metadata.copy()
                    chunk_metadata['chunk_index'] = len(chunks)
                    chunks.append({
                        'text': current_chunk.strip(),
                        'metadata': chunk_metadata
                    })
                    current_chunk = sentence
                else:
                    current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last remaining chunk
        if current_chunk:
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = len(chunks)
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': chunk_metadata
            })
        
        return chunks