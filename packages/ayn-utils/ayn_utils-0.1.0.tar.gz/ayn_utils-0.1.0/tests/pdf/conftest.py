import pytest
from pypdf import PdfWriter


@pytest.fixture
def create_dummy_pdf(tmp_path):
    def _create_dummy_pdf(name, num_pages):
        pdf_path = tmp_path / f"{name}.pdf"
        writer = PdfWriter()
        for _ in range(num_pages):
            writer.add_blank_page(width=612, height=792)
        with open(pdf_path, "wb") as f:
            writer.write(f)
        return pdf_path

    return _create_dummy_pdf
