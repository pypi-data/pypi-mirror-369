# rag_pipeline/document_loaders/word_loader.py
from docx import Document
from typing import List, Dict, Any
from pathlib import Path

class WordLoader:
    """Document loader for Word files (.docx)"""

    @staticmethod
    def load_folder(folder_path: str, extensions: List[str] = ['.docx']) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []
        for ext in extensions:
            for path in Path(folder_path).rglob(f"*{ext}"):
                try:
                    doc = Document(path)
                    text = '\n'.join([para.text for para in doc.paragraphs])
                    docs.append({
                        'text': text,
                        'metadata': {
                            'source': str(path),
                            'filename': path.name
                        }
                    })
                except Exception as e:
                    print(f"Error loading Word {path}: {e}")
        return docs
