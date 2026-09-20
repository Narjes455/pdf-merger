from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from pdf_merger import PDFMergeError, merge_pdfs, parse_page_range


def make_pdf(path: Path, pages: int) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    with path.open("wb") as f:
        writer.write(f)
    return path


def test_parse_all_pages():
    assert parse_page_range(None, 3) == [0, 1, 2]


def test_parse_mixed_ranges():
    assert parse_page_range("1-2,4,6-", 7) == [0, 1, 3, 5, 6]


def test_parse_invalid_range():
    with pytest.raises(PDFMergeError):
        parse_page_range("5", 3)


def test_parse_non_numeric():
    with pytest.raises(PDFMergeError):
        parse_page_range("abc", 3)


def test_merge_all_pages(tmp_path):
    a = make_pdf(tmp_path / "a.pdf", 2)
    b = make_pdf(tmp_path / "b.pdf", 3)
    out = tmp_path / "out.pdf"

    assert merge_pdfs([a, b], out) == 5
    assert len(PdfReader(str(out)).pages) == 5


def test_merge_with_ranges_and_bookmarks(tmp_path):
    a = make_pdf(tmp_path / "a.pdf", 4)
    b = make_pdf(tmp_path / "b.pdf", 2)
    out = tmp_path / "out.pdf"

    assert merge_pdfs([a, b], out, ranges=["1-2", None]) == 4
    titles = [item.title for item in PdfReader(str(out)).outline]
    assert titles == ["a", "b"]


def test_missing_file(tmp_path):
    with pytest.raises(PDFMergeError):
        merge_pdfs([tmp_path / "nope.pdf"], tmp_path / "out.pdf")


def test_output_cannot_be_input(tmp_path):
    a = make_pdf(tmp_path / "a.pdf", 1)
    with pytest.raises(PDFMergeError):
        merge_pdfs([a], a)
