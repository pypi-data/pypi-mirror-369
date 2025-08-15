from pypdf import PdfReader
from pdf.operations.merge import PDFMerger


def test_merge_pdfs(create_dummy_pdf, tmp_path):
    merger = PDFMerger()
    pdf1_path = create_dummy_pdf("pdf1", 2)
    pdf2_path = create_dummy_pdf("pdf2", 3)
    output_path = tmp_path / "merged.pdf"

    merger.merge_pdfs([pdf1_path, pdf2_path], output_path)

    assert output_path.exists()
    reader = PdfReader(output_path)
    assert len(reader.pages) == 5
