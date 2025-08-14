# rag_pipeline/vector_stores/chromadb.py
from typing import List, Dict, Any, Optional
from .base import VectorStore

class ChromaDBVectorStore(VectorStore):
    """ChromaDB vector store implementation."""
    
    def __init__(self, collection_name: str, persist_directory: str = "./chroma_db"):
        super().__init__(collection_name)
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Initialize ChromaDB client."""
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=self.persist_directory)
        except ImportError:
            raise ImportError("chromadb is required for ChromaDBVectorStore")
    
    def create_collection(self, dimension: int, distance_metric: str = "cosine", **kwargs) -> bool:
        """Create a new collection in ChromaDB."""
        try:
            # Chroma distance functions are l2, ip, cosine
            distance_map = {
                "cosine": "cosine",
                "euclidean": "l2",
                "dot": "ip"
            }
            chroma_distance = distance_map.get(distance_metric, "cosine")
            
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": chroma_distance}
            )
            return True
        except Exception as e:
            print(f"Error creating/getting collection: {e}")
            return False
    
    def add_documents(self, texts: List[str], embeddings: List[List[float]], 
                     metadatas: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Add documents to ChromaDB collection."""
        try:
            ids = [f"doc_{i}" for i in range(len(texts))]
            
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas or ([{}] * len(texts)),
                ids=ids
            )
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def search(self, query_embedding: List[float], top_k: int = 5, 
              similarity_threshold: float = 0.0, **kwargs) -> List[Dict[str, Any]]:
        """Search in ChromaDB collection."""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            search_results = []
            if not results['documents'] or not results['documents'][0]:
                return []

            for i in range(len(results['documents'][0])):
                # For cosine distance, similarity = 1 - distance
                score = 1 - results['distances'][0][i]
                if score >= similarity_threshold:
                    search_results.append({
                        'text': results['documents'][0][i],
                        'score': score,
                        'metadata': results['metadatas'][0][i] or {}
                    })
            
            return search_results
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def delete_collection(self) -> bool:
        """Delete ChromaDB collection."""
        try:
            self.client.delete_collection(self.collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False