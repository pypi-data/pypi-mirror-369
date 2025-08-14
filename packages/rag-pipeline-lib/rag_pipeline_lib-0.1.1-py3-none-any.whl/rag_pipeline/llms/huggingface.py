# rag_pipeline/llms/huggingface.py
from typing import List, Optional
from .base import LLM

class HuggingFaceLLM(LLM):
    """HuggingFace LLM implementation."""
    
    def __init__(self, model_name: str = "tiiuae/falcon-7b-instruct"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load HuggingFace model."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        except ImportError:
            raise ImportError("transformers is required for HuggingFaceLLM")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                temperature: float = 0.7, max_tokens: int = 512, **kwargs) -> str:
        """Generate response using HuggingFace."""
        try:
            import torch
            
            full_prompt = prompt
            if system_prompt:
                # Many models don't have a formal system prompt, so we prepend it.
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            inputs = self.tokenizer.encode(full_prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    **kwargs
                )
            
            response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            return response.strip()
        except Exception as e:
            print(f"Error generating with HuggingFace: {e}")
            return ""
    
    def generate_with_context(self, query: str, contexts: List[str], 
                            system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate response with retrieved contexts."""
        context_text = "\n\n".join([f"Context: {ctx}" for ctx in contexts])
        
        if system_prompt is None:
            system_prompt = "Answer the question based on the provided contexts."
        
        prompt = f"{context_text}\n\nQuestion: {query}\nAnswer:"
        
        return self.generate(prompt, system_prompt, **kwargs)