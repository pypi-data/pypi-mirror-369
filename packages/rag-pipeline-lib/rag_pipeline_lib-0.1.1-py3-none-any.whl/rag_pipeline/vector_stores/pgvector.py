# rag_pipeline/vector_stores/pgvector.py

import psycopg2
from pgvector.psycopg2 import register_vector
from .base import VectorStore

class PGVectorStore(VectorStore):
    def __init__(self, collection_name, host="localhost", port=5432, user="postgres", password="postgres", database="ragdb"):
        super().__init__(collection_name)
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=database
        )
        register_vector(self.conn)
        self.cursor = self.conn.cursor()

    def create_collection(self, dimension, distance_metric="cosine", **kwargs):
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.collection_name} (
            id SERIAL PRIMARY KEY,
            text TEXT,
            metadata JSONB,
            embedding VECTOR({dimension})
        )
        """)
        self.conn.commit()
        return True

    def add_documents(self, texts, embeddings, metadatas=None):
        for i in range(len(texts)):
            text = texts[i]
            emb = embeddings[i]
            meta = metadatas[i] if metadatas else {}
            self.cursor.execute(
                f"INSERT INTO {self.collection_name} (text, metadata, embedding) VALUES (%s, %s, %s)",
                (text, psycopg2.extras.Json(meta), emb)
            )
        self.conn.commit()
        return True

    def search(self, query_embedding, top_k=5, similarity_threshold=0.0, **kwargs):
        self.cursor.execute(
            f"""
            SELECT text, metadata, 1 - (embedding <=> %s) AS score
            FROM {self.collection_name}
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (query_embedding, query_embedding, top_k)
        )
        results = self.cursor.fetchall()
        return [
            {"text": r[0], "metadata": r[1], "score": float(r[2])}
            for r in results if r[2] > similarity_threshold
        ]

    def delete_collection(self):
        self.cursor.execute(f"DROP TABLE IF EXISTS {self.collection_name}")
        self.conn.commit()
        return True
