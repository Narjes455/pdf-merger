"""PDF Merger - merge multiple PDF files into one, with optional page ranges."""

from .core import PDFMergeError, merge_pdfs, parse_page_range

__all__ = ["merge_pdfs", "parse_page_range", "PDFMergeError"]
__version__ = "1.0.0"
