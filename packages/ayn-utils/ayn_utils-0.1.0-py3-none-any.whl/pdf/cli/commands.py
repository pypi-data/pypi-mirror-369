import click
from ..operations.merge import PDFMerger
from ..operations.split import PDFSplitter
from ..operations.rotate import PDFRotator
from ..core.exceptions import PDFToolError


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input", nargs=-1, required=True)
@click.option("-o", "--output", required=True, help="Output PDF file")
def merge(input, output):
    """Merge multiple PDF files into one"""
    try:
        merger = PDFMerger()
        merger.merge_pdfs(list(input), output)
    except PDFToolError as e:
        click.echo(f"Error: {e}", err=True)

    click.echo(f"Successfully merged {len(input)} PDFs into {output}")


@cli.command()
@click.argument("input", required=True)
@click.option("-o", "--output-dir", required=True, help="Output directory")
@click.option("-p", "--pages-per-file", default=1, help="Pages per output file")
def split(input, output_dir, pages_per_file):
    """Split a PDF into multiple files"""
    try:
        splitter = PDFSplitter()
        splitter.split_pdf(input, output_dir, pages_per_file)
    except PDFToolError as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("input", required=True)
@click.option("-o", "--output", required=True, help="Output PDF file")
@click.option("-s", "--start-page", type=int, required=True, help="Start page number")
@click.option("-e", "--end-page", type=int, required=True, help="End page number")
def extract_pages(input, output, start_page, end_page):
    """Extract specific pages from a PDF"""
    try:
        splitter = PDFSplitter()
        splitter.extract_pages(input, output, start_page, end_page)
    except PDFToolError as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("input", required=True)
@click.option("-o", "--output", required=True, help="Output PDF file")
@click.option(
    "-r",
    "--rotation",
    type=click.Choice(["90", "180", "270"]),
    required=True,
    help="Rotation angle in degrees",
)
def rotate(input, output, rotation):
    """Rotate PDF pages"""
    try:
        rotator = PDFRotator()
        rotator.rotate_pdf(input, output, int(rotation))
    except PDFToolError as e:
        click.echo(f"Error: {e}", err=True)
