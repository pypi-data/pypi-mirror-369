from typing import List, Optional
from .base import LLM

class LlamaCppServerLLM(LLM):
    """llama.cpp HTTP Server API üzerinden LLM yanıtı alma."""

    def __init__(self, model: str = "llama", base_url: str = "http://localhost:8080"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                temperature: float = 0.7, max_tokens: int = 512, **kwargs) -> str:
        """llama.cpp server ile doğrudan prompt gönderimi."""
        try:
            import requests
    
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"
    
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "temperature": temperature,
                "n_predict": max_tokens,
                "cache_prompt": True,
                "stop": ["\n\nEnglish:", "English:", "\n\n"],
                **kwargs
            }
    
            response = requests.post(f"{self.base_url}/v1/completions", json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["text"].strip()
    
        except Exception as e:
            print(f"Error generating with llama.cpp server: {e}")
            return ""


    def generate_with_context(self, query: str, contexts: List[str],
                              system_prompt: Optional[str] = None, **kwargs) -> str:
        """RAG için context + query içeren prompt ile LLM çağrısı."""
        context_text = "\n\n".join([f"Context {i+1}: {ctx}" for i, ctx in enumerate(contexts)])

        if system_prompt is None:
            system_prompt = (
                "You are a helpful assistant. Answer the user's question based on the provided contexts. "
                "If the context does not contain the answer, say you don't know."
            )

        prompt = f"Contexts:\n{context_text}\n\nQuestion: {query}\n\nAnswer:"
        return self.generate(prompt, system_prompt, **kwargs)
