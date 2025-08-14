import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from .base import VectorStore

class FaissVectorStore(VectorStore):
    """FAISS tabanlı, bellek içi basit vector store."""

    def __init__(
        self,
        collection_name: str,
        dimension: int,
        index_factory: str = "Flat",
        metric: str = "L2"
    ):
        super().__init__(collection_name)
        self.dimension = dimension
        metric_type = faiss.METRIC_L2 if metric.upper() == "L2" else faiss.METRIC_INNER_PRODUCT
        self.index = faiss.index_factory(dimension, index_factory, metric_type)
        self.id_map = faiss.IndexIDMap(self.index)
        self._metadatas: Dict[int, Dict[str, Any]] = {}

    def create_collection(self, dimension: int, **kwargs) -> bool:
        return True

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        # Default empty metadatas if None
        if metadatas is None:
            metadatas = [{}] * len(texts)

        # Sanity check
        if not (len(texts) == len(embeddings) == len(metadatas)):
            raise ValueError(
                f"[FaissVectorStore] Length mismatch: texts={len(texts)}, embeddings={len(embeddings)}, metadatas={len(metadatas)}"
            )

        # Compute new IDs
        ids = list(range(len(self._metadatas), len(self._metadatas) + len(embeddings)))
        xb = np.array(embeddings, dtype="float32")
        self.id_map.add_with_ids(xb, np.array(ids))

        # Save metadata with correct local index
        for idx, text, md in zip(ids, texts, metadatas):
            self._metadatas[idx] = {**md, "text": text}

        return True

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.0,
        **kwargs
    ) -> List[Dict[str, Any]]:
        xq = np.array([query_embedding], dtype="float32")
        D, I = self.id_map.search(xq, top_k)
        results: List[Dict[str, Any]] = []
    
        print("\n[FAISS DEBUG] Retrieval Results:")
        for rank, (dist, idx) in enumerate(zip(D[0], I[0]), start=1):
            if idx < 0:
                continue
            score = 1.0 / (1.0 + dist)
            if score < similarity_threshold:
                continue
            md = self._metadatas.get(int(idx), {})
            
            # --- HATA ANALİZİ İÇİN LOG ---
            print(f"\n------------------------------")
            print(f"Rank: {rank}")
            print(f"Score: {score:.4f}")
            print(f"Raw Distance: {dist:.4f}")
            print(f"Chunk ID: {idx}")
            print(f"Metadata: {json.dumps(md, ensure_ascii=False)}")
            print(f"Chunk Preview: {md.get('text', '')[:300]}")
            print("------------------------------")
    
            results.append({
                "text": md.get("text", ""),
                "score": score,
                "metadata": {k: v for k, v in md.items() if k != "text"}
            })
    
        return results


    def delete_collection(self) -> bool:
        self.id_map.reset()
        self._metadatas.clear()
        return True

    def save_to_disk(self, index_path: str, metadata_path: str) -> None:
        faiss.write_index(self.id_map, index_path)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(self._metadatas, f, ensure_ascii=False, indent=2)

    def load_from_disk(self, index_path: str, metadata_path: str) -> None:
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index file not found: {index_path}")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        self.id_map = faiss.read_index(index_path)
        with open(metadata_path, "r", encoding="utf-8") as f:
            self._metadatas = {int(k): v for k, v in json.load(f).items()}
