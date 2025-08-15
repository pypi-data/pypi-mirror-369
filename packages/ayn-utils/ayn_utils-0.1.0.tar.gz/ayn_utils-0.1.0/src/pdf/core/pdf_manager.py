import os
from pypdf import PdfReader
from .exceptions import (
    FileNotFoundError,
    InvalidPDFError,
    PageRangeError,
)


class PDFManager:
    """Handles basic PDF file operations"""

    def __init__(self):
        self.readers = {}

    def load_pdf(self, filepath: str) -> PdfReader:
        """Load a PDF file and return a PdfReader object"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"PDF file not found: {filepath}")

        try:
            if filepath not in self.readers:
                self.readers[filepath] = PdfReader(filepath)
            return self.readers[filepath]
        except Exception as e:
            raise InvalidPDFError(f"Invalid PDF file: {filepath}. Error: {str(e)}")

    def get_page_count(self, filepath: str) -> int:
        """Get the number of pages in a PDF"""
        reader = self.load_pdf(filepath)
        return len(reader.pages)

    def validate_page_range(self, filepath: str, start: int, end: int) -> None:
        """Validate that page range is within PDF bounds"""
        page_count = self.get_page_count(filepath)
        if start < 1 or end > page_count or start > end:
            raise PageRangeError(
                f"Invalid page range {start}-{end}. PDF has {page_count} pages."
            )
