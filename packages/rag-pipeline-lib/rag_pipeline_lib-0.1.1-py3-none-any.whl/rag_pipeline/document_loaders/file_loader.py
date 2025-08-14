# rag_pipeline/document_loaders/file_loader.py
import os
from typing import List, Dict, Any
from pathlib import Path

class DocumentLoader:
    """Document loader for text files (.txt, .md)"""
    
    @staticmethod
    def load_file(file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                'text': content,
                'metadata': {
                    'source': file_path,
                    'filename': os.path.basename(file_path)
                }
            }
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return {'text': '', 'metadata': {}}
    
    @staticmethod
    def load_files(file_paths: List[str]) -> List[Dict[str, Any]]:
        documents: List[Dict[str, Any]] = []
        for path in file_paths:
            doc = DocumentLoader.load_file(path)
            if doc['text']:
                documents.append(doc)
        return documents
    
    @staticmethod
    def load_folder(folder_path: str, extensions: List[str] = ['.txt', '.md']) -> List[Dict[str, Any]]:
        folder = Path(folder_path)
        if not folder.is_dir():
            print(f"Folder not found: {folder_path}")
            return []
        file_paths: List[str] = []
        for ext in extensions:
            file_paths.extend(str(p) for p in folder.rglob(f"*{ext}"))
        return DocumentLoader.load_files(file_paths)
