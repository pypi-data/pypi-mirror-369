# RAG Pipeline

RAG Pipeline, Retrieval-Augmented Generation (RAG) mimarisi ile metin tabanlı arama ve yanıt üretme işlemlerini kolaylaştıran bir Python kütüphanesidir.  
Bu kütüphane ile belgelerinizi indeksleyebilir, FAISS veya diğer vektör veri tabanlarıyla arama yapabilir ve LLM modelleri ile entegre edebilirsiniz.

---

## 📦 Kurulum

PyPI üzerinden:
```bash
pip install rag-pipeline-lib
```

Yerel geliştirme modu (kaynak kodu değiştirip test etmek için):
```bash
git clone https://github.com/kullaniciadi/rag_pipeline.git
cd rag_pipeline
pip install -e .
```

---

## 🚀 Quickstart

```python
from rag_pipeline import RAGPipeline, FixedSizeChunking
from rag_pipeline.document_loaders import PDFLoader
from rag_pipeline.embeddings import OllamaEmbeddings
from rag_pipeline.llms import OllamaLLM
from rag_pipeline.vector_stores import FAISSVectorStore

# Bileşenleri başlat
embedding = OllamaEmbeddings("nomic-embed-text:latest", base_url="http://ollama:11434")
vector_store = FAISSVectorStore(collection_name="my_collection", dimension=768)
llm = OllamaLLM("llama3.2:3b", base_url="http://ollama:11434")
chunking = FixedSizeChunking(chunk_size=450, overlap=100)

# Pipeline oluştur
rag = RAGPipeline(vector_store, embedding, llm, chunking)

# Belgeleri yükle
docs = PDFLoader.load_folder("./documents")
rag.add_documents(docs)

# Sorgu yap
print(rag.query("What are the feature methods used in cattle identification?"))
```

---

##  Proje Yapısı

```
rag_pipeline/
│
├── rag_pipeline/
│   ├── __init__.py
│   ├── pipeline.py
│   ├── chunking/
│   ├── document_loaders/
│   ├── embeddings/
│   ├── llms/
│   ├── vector_stores/
│   └── retrievers/
│
├── tests/
│
├── setup.py
├── pyproject.toml
├── LICENSE
└── README.md
```

---

##  Lisans

Bu proje **MIT Lisansı** ile lisanslanmıştır.  
Tüm detaylar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.

```
MIT License

Copyright (c) 2025 İsim

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

---

## Özellikler

- FAISS ve diğer vektör veritabanı desteği
- Hibrit retrieval desteği (BM25 + vektör arama)
- Modüler yapı
- Geliştirici dostu API

---

##  Katkıda Bulunma

1. Bu projeyi forklayın
2. Yeni bir branch oluşturun (`git checkout -b feature/ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch’inizi push edin (`git push origin feature/ozellik`)
5. Pull Request oluşturun

---

## İletişim

Sorularınız veya önerileriniz için: **ornek@email.com**
