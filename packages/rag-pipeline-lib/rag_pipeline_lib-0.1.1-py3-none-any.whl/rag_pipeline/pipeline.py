# rag_pipeline/pipeline.py
from typing import List, Dict, Any, Optional
from .vector_stores import VectorStore
from .embeddings import Embedding
from .llms import LLM
from .chunking import ChunkingStrategy, FixedSizeChunking
from .document_loaders import DocumentLoader
from .retrievers.bm25 import BM25Retriever  # <-- Hibrit için

def _minmax_norm(values: List[float]) -> List[float]:
    """[v] -> [0,1] normalize. Tümü aynıysa 1.0 döner."""
    if not values:
        return []
    vmin, vmax = min(values), max(values)
    if vmax - vmin == 0:
        return [1.0 for _ in values]
    return [(v - vmin) / (vmax - vmin) for v in values]

class RAGPipeline:
    """Main RAG pipeline orchestrator (Hybrid Retrieval destekli)."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding: Embedding, 
        llm: LLM,
        chunking_strategy: Optional[ChunkingStrategy] = None
    ):
        self.vector_store = vector_store
        self.embedding = embedding
        self.llm = llm
        self.chunking_strategy = chunking_strategy or FixedSizeChunking()

        # --- Hibrit Retrieval için sparse taraf ---
        self._bm25 = BM25Retriever()
        self._all_chunks: List[Dict[str, Any]] = []  # {'text': str, 'metadata': dict}

        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize vector store collection."""
        dimension = self.embedding.get_dimension()
        if dimension > 0:
            self.vector_store.create_collection(dimension)
        else:
            raise ValueError("Could not determine embedding dimension. Pipeline initialization failed.")

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Chunk, embed, and add documents to the vector store."""
        all_chunks_text: List[str] = []
        all_embeddings: List[List[float]] = []
        all_metadatas: List[Dict[str, Any]] = []
        
        for doc in documents:
            chunks = self.chunking_strategy.chunk_text(
                doc.get('text', ''), 
                doc.get('metadata', {})
            )
            chunk_texts = [c['text'] for c in chunks if c.get('text')]
            if not chunk_texts:
                continue

            embeddings = self.embedding.embed_texts(chunk_texts) or []

            # Boş embedding/geçersizleri filtrele (sağlamlık)
            for c, e in zip(chunks, embeddings):
                if e and isinstance(e, list) and len(e) > 0:
                    all_chunks_text.append(c['text'])
                    all_embeddings.append(e)
                    all_metadatas.append(c.get('metadata', {}))

        if not all_chunks_text:
            print("No text to add to the vector store.")
            return False

        # --- Dense tarafı: vektör veritabanına ekle ---
        ok = self.vector_store.add_documents(all_chunks_text, all_embeddings, all_metadatas)

        # --- Sparse tarafı: BM25 indeksi güncelle ---
        if ok:
            for t, m in zip(all_chunks_text, all_metadatas):
                self._all_chunks.append({"text": t, "metadata": m})
            if self._all_chunks:
                self._bm25.build(self._all_chunks)

        return ok
    
    def add_files(self, file_paths: List[str]) -> bool:
        """Load and add files to the RAG pipeline."""
        documents = DocumentLoader.load_files(file_paths)
        if not documents:
            print("No documents were loaded from the provided file paths.")
            return False
        return self.add_documents(documents)
    
    def add_folder(self, folder_path: str, extensions: List[str] = ['.txt']) -> bool:
        """Load and add all files from a folder to the RAG pipeline."""
        documents = DocumentLoader.load_folder(folder_path, extensions)
        if not documents:
            print(f"No documents with extensions {extensions} found in folder '{folder_path}'.")
            return False
        return self.add_documents(documents)
    
    def query(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.0,
        system_prompt: Optional[str] = None,
        # --- Hibrit parametreleri ---
        hybrid: bool = True,
        alpha: float = 0.6,          # dense ağırlığı
        sparse_k: Optional[int] = None,
        dense_k: Optional[int] = None,
        **llm_kwargs
    ) -> Dict[str, Any]:
        """Hybrid (dense + BM25) sorgu. hybrid=False => sadece dense."""
        # 1) DENSE
        query_embedding = self.embedding.embed_text(query)
        if not query_embedding:
            return {
                'answer': "Failed to generate an embedding for the query.",
                'contexts': [],
                'scores': [],
                'metadata': []
            }

        dk = dense_k or top_k
        dense_results = self.vector_store.search(
            query_embedding, top_k=dk, similarity_threshold=similarity_threshold
        ) or []

        if not hybrid:
            contexts = [r['text'] for r in dense_results]
            scores   = [r['score'] for r in dense_results]
            answer = self.llm.generate_with_context(
                query, contexts, system_prompt=system_prompt, **llm_kwargs
            )
            return {
                'answer': answer,
                'contexts': contexts,
                'scores': scores,
                'metadata': [r.get('metadata', {}) for r in dense_results]
            }

        # 2) SPARSE (BM25)
        sk = sparse_k or top_k
        sparse_results = self._bm25.topk(query, k=sk) if self._all_chunks else []

        # 3) Skor normalize + birleştir (Linear Fusion)
        d_texts = [r['text'] for r in dense_results]
        d_norm  = _minmax_norm([r['score'] for r in dense_results])
        d_map   = {t: s for t, s in zip(d_texts, d_norm)}

        s_texts = [r['text'] for r in sparse_results]
        s_norm  = _minmax_norm([r['score'] for r in sparse_results])
        s_map   = {t: s for t, s in zip(s_texts, s_norm)}

        pool = set(d_map.keys()) | set(s_map.keys())
        fused: List[Dict[str, Any]] = []
        for t in pool:
            ds = d_map.get(t, 0.0)
            ss = s_map.get(t, 0.0)
            final = alpha * ds + (1 - alpha) * ss

            # metadata’yı ilk bulunan kaynaktan al
            meta = {}
            for r in dense_results:
                if r['text'] == t:
                    meta = r.get('metadata', {})
                    break
            if not meta:
                for r in sparse_results:
                    if r['text'] == t:
                        meta = r.get('metadata', {})
                        break

            fused.append({"text": t, "score": final, "metadata": meta})

        fused_sorted = sorted(fused, key=lambda x: x['score'], reverse=True)[:top_k]

        # 4) LLM cevabı
        contexts = [r['text'] for r in fused_sorted]
        scores   = [r['score'] for r in fused_sorted]
        answer = self.llm.generate_with_context(
            query, contexts, system_prompt=system_prompt, **llm_kwargs
        )

        return {
            'answer': answer,
            'contexts': contexts,
            'scores': scores,
            'metadata': [r.get('metadata', {}) for r in fused_sorted]
        }
    
    def clear_collection(self) -> bool:
        """Clear the vector store collection."""
        # Dense tarafını temizle
        ok = self.vector_store.delete_collection()
        # Sparse tarafını da temizle
        self._all_chunks.clear()
        self._bm25 = BM25Retriever()
        return ok
