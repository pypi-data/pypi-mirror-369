from pypdf import PdfReader
from pdf.operations.split import PDFSplitter


def test_split_pdf(create_dummy_pdf, tmp_path):
    splitter = PDFSplitter()
    input_pdf_path = create_dummy_pdf("test_split", 10)
    output_dir = tmp_path / "split_output"
    output_dir.mkdir()

    splitter.split_pdf(input_pdf_path, output_dir, pages_per_file=2)

    # Expected number of output files is 10 / 2 = 5
    output_files = list(output_dir.glob("*.pdf"))
    assert len(output_files) == 5

    # Check the number of pages in each split file
    for pdf_file in output_files:
        reader = PdfReader(pdf_file)
        assert len(reader.pages) == 2


def test_split_pdf_with_remainder(create_dummy_pdf, tmp_path):
    splitter = PDFSplitter()
    input_pdf_path = create_dummy_pdf("test_split_remainder", 7)
    output_dir = tmp_path / "split_output_remainder"
    output_dir.mkdir()

    splitter.split_pdf(input_pdf_path, output_dir, pages_per_file=3)

    # Expected number of output files is ceil(7 / 3) = 3
    output_files = sorted(list(output_dir.glob("*.pdf")))
    assert len(output_files) == 3

    # Check pages in each file
    reader1 = PdfReader(output_files[0])
    assert len(reader1.pages) == 3
    reader2 = PdfReader(output_files[1])
    assert len(reader2.pages) == 3
    reader3 = PdfReader(output_files[2])
    assert len(reader3.pages) == 1
