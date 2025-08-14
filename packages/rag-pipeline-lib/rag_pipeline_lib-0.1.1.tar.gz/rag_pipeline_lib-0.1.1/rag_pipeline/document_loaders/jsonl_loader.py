
# rag_pipeline/document_loaders/jsonl_loader.py
import json
from typing import List, Dict, Any
from pathlib import Path

class JSONLLoader:
    """Document loader for JSONL files (.jsonl)"""

    @staticmethod
    def load_folder(folder_path: str, extensions: List[str] = ['.jsonl']) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []
        for ext in extensions:
            for path in Path(folder_path).rglob(f"*{ext}"):
                try:
                    text = ''
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            obj = json.loads(line)
                            text += obj.get('text', obj.get('content', '')) + '\n'
                    docs.append({
                        'text': text,
                        'metadata': {
                            'source': str(path),
                            'filename': path.name
                        }
                    })
                except Exception as e:
                    print(f"Error loading JSONL {path}: {e}")
        return docs
