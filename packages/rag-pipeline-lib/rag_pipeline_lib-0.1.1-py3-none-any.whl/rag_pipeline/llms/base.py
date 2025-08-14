# rag_pipeline/llms/base.py
from abc import ABC, abstractmethod
from typing import List, Optional

class LLM(ABC):
    """Abstract base class for LLMs."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate response from prompt."""
        pass
    
    @abstractmethod
    def generate_with_context(self, query: str, contexts: List[str], 
                            system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate response with retrieved contexts."""
        pass