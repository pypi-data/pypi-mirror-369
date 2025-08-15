from pypdf import PdfWriter
from ..core.pdf_manager import PDFManager
from ..core.exceptions import PDFToolError


class PDFRotator:
    """Handles PDF rotation operations"""

    def __init__(self):
        self.pdf_manager = PDFManager()

    def rotate_pdf(self, input_file: str, output_file: str, rotation: int) -> None:
        """Rotate all pages in a PDF by specified degrees"""
        if rotation not in [90, 180, 270]:
            raise PDFToolError("Rotation must be 90, 180, or 270 degrees")

        reader = self.pdf_manager.load_pdf(input_file)
        writer = PdfWriter()

        try:
            for page in reader.pages:
                rotated_page = page.rotate(rotation)
                writer.add_page(rotated_page)

            with open(output_file, "wb") as output:
                writer.write(output)

            print(f"Successfully rotated PDF by {rotation} degrees: {output_file}")

        except Exception as e:
            raise PDFToolError(f"Error rotating PDF: {str(e)}")
