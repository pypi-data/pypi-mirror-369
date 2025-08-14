from .file_loader import DocumentLoader
from .pdf_loader import PDFLoader
from .csv_loader import CSVLoader
from .jsonl_loader import JSONLLoader
from .excel_loader import ExcelLoader    # <-- yeni ekle
from .word_loader import WordLoader      # <-- yeni ekle

__all__ = [
    'DocumentLoader',
    'PDFLoader',
    'CSVLoader',
    'JSONLLoader',
    'ExcelLoader',   # <-- yeni ekle
    'WordLoader',    # <-- yeni ekle
]
