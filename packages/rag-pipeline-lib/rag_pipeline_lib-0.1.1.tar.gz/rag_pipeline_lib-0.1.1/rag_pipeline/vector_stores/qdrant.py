# rag_pipeline/vector_stores/qdrant.py
from typing import List, Dict, Any, Optional
from .base import VectorStore

class QdrantVectorStore(VectorStore):
    """Qdrant vector store implementation."""
    
    def __init__(self, collection_name: str, host: str = "localhost", 
                 port: int = 6333, api_key: Optional[str] = None):
        super().__init__(collection_name)
        self.host = host
        self.port = port
        self.api_key = api_key
        self.client = None
        self._connect()
    
    def _connect(self):
        """Initialize Qdrant client."""
        try:
            from qdrant_client import QdrantClient
            
            if self.api_key:
                self.client = QdrantClient(
                    host=self.host, 
                    port=self.port, 
                    api_key=self.api_key
                )
            else:
                self.client = QdrantClient(host=self.host, port=self.port)
        except ImportError:
            raise ImportError("qdrant-client is required for QdrantVectorStore")
    
    def create_collection(self, dimension: int, distance_metric: str = "cosine", **kwargs) -> bool:
        """Create a new collection in Qdrant."""
        from qdrant_client.models import Distance, VectorParams
        
        distance_map = {
            "cosine": Distance.COSINE,
            "euclidean": Distance.EUCLID,
            "dot": Distance.DOT
        }
        
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=distance_map.get(distance_metric, Distance.COSINE),
                )
            )
            return True
        except Exception as e:
            # Collection might already exist, which is not a critical error for pipeline setup
            if "already exists" in str(e):
                return True
            print(f"Error creating collection: {e}")
            return False
    
    def add_documents(self, texts: List[str], embeddings: List[List[float]], 
                     metadatas: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Add documents to Qdrant collection."""
        from qdrant_client.models import PointStruct
        
        try:
            points = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                metadata = metadatas[i] if metadatas else {}
                metadata['text'] = text
                
                points.append(
                    PointStruct(
                        id=i,
                        vector=embedding,
                        payload=metadata
                    )
                )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True
            )
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def search(self, query_embedding: List[float], top_k: int = 5, 
              similarity_threshold: float = 0.0, **kwargs) -> List[Dict[str, Any]]:
        """Search in Qdrant collection."""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=similarity_threshold
            )
            
            return [
                {
                    'text': result.payload.get('text', ''),
                    'score': result.score,
                    'metadata': {k: v for k, v in result.payload.items() if k != 'text'}
                }
                for result in results
            ]
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def delete_collection(self) -> bool:
        """Delete Qdrant collection."""
        try:
            self.client.delete_collection(self.collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False