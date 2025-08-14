from typing import List
from .base import LLM
from openai import OpenAI
import os

class OpenAILLM(LLM):
    """OpenAI LLM implementation."""
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        
        # Environment variable'dan API anahtarını al
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        
        self.client = OpenAI(api_key=api_key)
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def generate_with_system_prompt(self, system_prompt: str, user_prompt: str, max_tokens: int = 500) -> str:
        """Generate text with system prompt using OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def generate_with_context(self, query: str, contexts: List[str], system_prompt: str = None, max_tokens: int = 500) -> str:
        """Generate text with context using OpenAI."""
        # Context'leri birleştir
        context_text = "\n\n".join(contexts)
        
        # Prompt'u oluştur
        if system_prompt:
            prompt = f"Context:\n{context_text}\n\nQuestion: {query}"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
        else:
            prompt = f"Based on the following context, answer the question:\n\nContext:\n{context_text}\n\nQuestion: {query}\n\nAnswer:"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
        
        return response.choices[0].message.content