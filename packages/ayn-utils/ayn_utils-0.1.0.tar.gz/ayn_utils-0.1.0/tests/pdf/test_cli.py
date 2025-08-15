from click.testing import CliRunner
from pypdf import PdfReader
from pdf.cli.commands import cli


def test_merge_command(create_dummy_pdf, tmp_path):
    runner = CliRunner()
    pdf1 = create_dummy_pdf("doc1", 2)
    pdf2 = create_dummy_pdf("doc2", 3)
    output_pdf = tmp_path / "merged.pdf"

    result = runner.invoke(cli, ["merge", str(pdf1), str(pdf2), "-o", str(output_pdf)])

    assert result.exit_code == 0
    assert output_pdf.exists()
    reader = PdfReader(output_pdf)
    assert len(reader.pages) == 5


def test_split_command(create_dummy_pdf, tmp_path):
    runner = CliRunner()
    input_pdf = create_dummy_pdf("doc_to_split", 5)
    output_dir = tmp_path / "split_output"
    output_dir.mkdir()

    result = runner.invoke(
        cli, ["split", str(input_pdf), "-o", str(output_dir), "-p", "2"]
    )
    assert result.exit_code == 0

    # Expected number of output files is ceil(5 / 2) = 3
    output_files = sorted(list(output_dir.glob("*.pdf")))
    assert len(output_files) == 3

    # Check pages in each file
    reader1 = PdfReader(output_files[0])
    assert len(reader1.pages) == 2
    reader2 = PdfReader(output_files[1])
    assert len(reader2.pages) == 2
    reader3 = PdfReader(output_files[2])
    assert len(reader3.pages) == 1


def test_extract_pages_command(create_dummy_pdf, tmp_path):
    runner = CliRunner()
    input_pdf = create_dummy_pdf("doc_to_extract", 10)
    output_pdf = tmp_path / "extracted.pdf"

    result = runner.invoke(
        cli,
        ["extract-pages", str(input_pdf), "-o", str(output_pdf), "-s", "2", "-e", "5"],
    )
    assert result.exit_code == 0
    assert output_pdf.exists()
    reader = PdfReader(output_pdf)
    assert len(reader.pages) == 4


def test_rotate_command(create_dummy_pdf, tmp_path):
    runner = CliRunner()
    input_pdf = create_dummy_pdf("doc_to_rotate", 3)
    output_pdf = tmp_path / "rotated.pdf"

    rotation_angle = 90
    result = runner.invoke(
        cli,
        ["rotate", str(input_pdf), "-o", str(output_pdf), "-r", str(rotation_angle)],
    )
    assert result.exit_code == 0
    assert output_pdf.exists()
    reader = PdfReader(output_pdf)
    assert len(reader.pages) == 3

    for page in reader.pages:
        assert page.get("/Rotate") == rotation_angle
