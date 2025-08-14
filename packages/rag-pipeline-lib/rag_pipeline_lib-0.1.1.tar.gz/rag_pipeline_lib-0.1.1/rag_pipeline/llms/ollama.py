# rag_pipeline/llms/ollama.py
from typing import List, Optional
from .base import LLM

class OllamaLLM(LLM):
    """Ollama LLM implementation."""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                temperature: float = 0.7, max_tokens: int = 512, **kwargs) -> str:
        """Generate response using Ollama."""
        try:
            import requests
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    **kwargs
                }
            }
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            
            return response.json()["response"]
        except Exception as e:
            print(f"Error generating with Ollama: {e}")
            return ""
    
    def generate_with_context(self, query: str, contexts: List[str], 
                            system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate response with retrieved contexts."""
        context_text = "\n\n".join([f"Context {i+1}: {ctx}" for i, ctx in enumerate(contexts)])
        
        if system_prompt is None:
            system_prompt = "You are a helpful assistant. Answer the user's question based on the provided contexts. If the context does not contain the answer, say you don't know."
        
        prompt = f"Contexts:\n{context_text}\n\nQuestion: {query}\n\nAnswer:"
        
        return self.generate(prompt, system_prompt, **kwargs)