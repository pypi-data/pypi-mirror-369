import pytest
from pypdf import PdfReader
from pdf.operations.rotate import PDFRotator


@pytest.mark.parametrize("rotation_angle", [90, 180, 270])
def test_rotate_pdf(create_dummy_pdf, tmp_path, rotation_angle):
    rotator = PDFRotator()
    input_pdf_path = create_dummy_pdf("test_rotate", 3)
    output_path = tmp_path / f"rotated_{rotation_angle}.pdf"

    rotator.rotate_pdf(input_pdf_path, output_path, rotation_angle)

    assert output_path.exists()
    reader = PdfReader(output_path)
    assert len(reader.pages) == 3

    for page in reader.pages:
        assert page.get("/Rotate") == rotation_angle
