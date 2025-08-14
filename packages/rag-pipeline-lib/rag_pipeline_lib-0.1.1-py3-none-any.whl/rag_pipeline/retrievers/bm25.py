# rag_pipeline/retrievers/bm25.py
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi

class BM25Retriever:
    """Basit BM25 retriever (sparse)."""
    def __init__(self):
        self.bm25 = None
        self._docs: List[Dict[str, Any]] = []
        self._tokenized = []

    def build(self, chunks: List[Dict[str, Any]]):
        """chunks: [{'text': str, 'metadata': {...}}, ...]"""
        self._docs = chunks
        self._tokenized = [c['text'].lower().split() for c in chunks]
        self.bm25 = BM25Okapi(self._tokenized)

    def topk(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if not self.bm25 or not self._docs:
            return []
        toks = query.lower().split()
        scores = self.bm25.get_scores(toks)
        # en yüksek k
        idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        out = []
        for i in idxs:
            out.append({
                "text": self._docs[i]["text"],
                "score": float(scores[i]),
                "metadata": self._docs[i].get("metadata", {})
            })
        return out
