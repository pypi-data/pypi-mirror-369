from pypdf import PdfReader
from pdf.operations.split import PDFSplitter


def test_extract_pages(create_dummy_pdf, tmp_path):
    splitter = PDFSplitter()
    input_pdf_path = create_dummy_pdf("test_extract", 10)
    output_path = tmp_path / "extracted.pdf"

    # Extract pages 2 to 5 (inclusive), which is 4 pages
    splitter.extract_pages(input_pdf_path, output_path, start_page=2, end_page=5)

    assert output_path.exists()
    reader = PdfReader(output_path)
    assert len(reader.pages) == 4


def test_extract_single_page(create_dummy_pdf, tmp_path):
    splitter = PDFSplitter()
    input_pdf_path = create_dummy_pdf("test_extract_single", 5)
    output_path = tmp_path / "extracted_single.pdf"

    # Extract page 3
    splitter.extract_pages(input_pdf_path, output_path, start_page=3, end_page=3)

    assert output_path.exists()
    reader = PdfReader(output_path)
    assert len(reader.pages) == 1
