"""Custom exceptions for PDF operations"""


class PDFToolError(Exception):
    """Base exception for PDF operations"""

    pass


class FileNotFoundError(PDFToolError):
    """Raised when a PDF file is not found"""

    pass


class InvalidPDFError(PDFToolError):
    """Raised when a file is not a valid PDF"""

    pass


class PageRangeError(PDFToolError):
    """Raised when page range is invalid"""

    pass
