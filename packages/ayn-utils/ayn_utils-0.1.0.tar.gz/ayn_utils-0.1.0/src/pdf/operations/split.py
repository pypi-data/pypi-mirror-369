import os
from pypdf import PdfWriter
from ..core.pdf_manager import PDFManager
from ..core.exceptions import PDFToolError


class PDFSplitter:
    """Handles PDF splitting operations"""

    def __init__(self):
        self.pdf_manager = PDFManager()

    def split_pdf(
        self, input_file: str, output_dir: str, pages_per_file: int = 1
    ) -> None:
        """Split a PDF into multiple files"""
        reader = self.pdf_manager.load_pdf(input_file)
        total_pages = len(reader.pages)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        base_name = os.path.splitext(os.path.basename(input_file))[0]

        try:
            for i in range(0, total_pages, pages_per_file):
                writer = PdfWriter()
                end_page = min(i + pages_per_file, total_pages)

                for page_num in range(i, end_page):
                    writer.add_page(reader.pages[page_num])

                output_filename = f"{base_name}_part_{i // pages_per_file + 1}.pdf"
                output_path = os.path.join(output_dir, output_filename)

                with open(output_path, "wb") as output_file:
                    writer.write(output_file)

            files_created = (total_pages + pages_per_file - 1) // pages_per_file
            print(f"Successfully split PDF into {files_created} files in {output_dir}")

        except Exception as e:
            raise PDFToolError(f"Error splitting PDF: {str(e)}")

    def extract_pages(
        self, input_file: str, output_file: str, start_page: int, end_page: int
    ) -> None:
        """Extract specific pages from a PDF"""
        reader = self.pdf_manager.load_pdf(input_file)
        self.pdf_manager.validate_page_range(input_file, start_page, end_page)

        writer = PdfWriter()

        try:
            for page_num in range(start_page - 1, end_page):
                writer.add_page(reader.pages[page_num])

            with open(output_file, "wb") as output:
                writer.write(output)

            page_count = end_page - start_page + 1
            print(f"Successfully extracted {page_count} pages to {output_file}")

        except Exception as e:
            raise PDFToolError(f"Error extracting pages: {str(e)}")
