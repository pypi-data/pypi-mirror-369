from typing import List
from pypdf import PdfWriter
from ..core.pdf_manager import PDFManager
from ..core.exceptions import PDFToolError


class PDFMerger:
    """Handles PDF merging operations"""

    def __init__(self):
        self.pdf_manager = PDFManager()

    def merge_pdfs(self, input_files: List[str], output_file: str) -> None:
        """Merge multiple PDF files into a single PDF"""
        if not input_files:
            raise PDFToolError("No input files provided for merging")

        writer = PdfWriter()

        try:
            for filepath in input_files:
                reader = self.pdf_manager.load_pdf(filepath)
                for page in reader.pages:
                    writer.add_page(page)

            with open(output_file, "wb") as output:
                writer.write(output)

        except Exception as e:
            raise PDFToolError(f"Error merging PDFs: {str(e)}")
