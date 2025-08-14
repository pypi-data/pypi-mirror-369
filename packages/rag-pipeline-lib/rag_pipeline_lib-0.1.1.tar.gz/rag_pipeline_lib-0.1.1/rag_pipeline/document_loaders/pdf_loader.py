# rag_pipeline/document_loaders/pdf_loader.py
import fitz  # PyMuPDF
from typing import List, Dict, Any
from pathlib import Path

class PDFLoader:
    """Document loader for PDF files (.pdf)"""

    @staticmethod
    def load_folder(folder_path: str, extensions: List[str] = ['.pdf']) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []
        for ext in extensions:
            for path in Path(folder_path).rglob(f"*{ext}"):
                try:
                    text = ''
                    doc = fitz.open(path)
                    for page in doc:
                        text += page.get_text()
                    docs.append({
                        'text': text,
                        'metadata': {
                            'source': str(path),
                            'filename': path.name
                        }
                    })
                except Exception as e:
                    print(f"Error loading PDF {path}: {e}")
        return docs

