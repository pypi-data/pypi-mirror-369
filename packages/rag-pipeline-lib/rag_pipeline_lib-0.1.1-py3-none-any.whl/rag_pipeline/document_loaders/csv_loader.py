# rag_pipeline/document_loaders/csv_loader.py
import csv
from typing import List, Dict, Any
from pathlib import Path

class CSVLoader:
    """Document loader for CSV files (.csv)"""

    @staticmethod
    def load_folder(folder_path: str, extensions: List[str] = ['.csv']) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []
        for ext in extensions:
            for path in Path(folder_path).rglob(f"*{ext}"):
                try:
                    with open(path, newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        text = '\n'.join([', '.join(row) for row in reader])
                    docs.append({
                        'text': text,
                        'metadata': {
                            'source': str(path),
                            'filename': path.name
                        }
                    })
                except Exception as e:
                    print(f"Error loading CSV {path}: {e}")
        return docs
