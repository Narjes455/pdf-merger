"""Core merging logic, independent of any user interface."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Sequence, Union

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

PathLike = Union[str, Path]


class PDFMergeError(Exception):
    """Raised when the merge cannot be completed."""


def parse_page_range(spec: Optional[str], total_pages: int) -> list[int]:
    """Convert a page spec like "1-3,5,8-" into zero-based page indexes.

    - None or "" means all pages.
    - "5-" means from page 5 to the end.
    - Pages are 1-based for the user and validated against total_pages.
    """
    if not spec or not spec.strip():
        return list(range(total_pages))

    pages: list[int] = []
    for part in spec.replace(" ", "").split(","):
        if not part:
            continue
        try:
            if "-" in part:
                start_s, end_s = part.split("-", 1)
                start = int(start_s) if start_s else 1
                end = int(end_s) if end_s else total_pages
            else:
                start = end = int(part)
        except ValueError:
            raise PDFMergeError(f"Invalid page range '{part}'") from None

        if start < 1 or end > total_pages or start > end:
            raise PDFMergeError(
                f"Invalid page range '{part}' (document has {total_pages} pages)"
            )
        pages.extend(range(start - 1, end))
    return pages


def merge_pdfs(
    inputs: Sequence[PathLike],
    output: PathLike,
    ranges: Optional[Iterable[Optional[str]]] = None,
    add_bookmarks: bool = True,
) -> int:
    """Merge PDFs in the given order and write them to `output`.

    Args:
        inputs: PDF file paths, in the order they should appear.
        output: Destination file path.
        ranges: Optional page spec per input (same length as inputs).
        add_bookmarks: Add a bookmark at the start of each source file.

    Returns:
        Total number of pages written.
    """
    if not inputs:
        raise PDFMergeError("No input files were provided")

    range_list = list(ranges) if ranges is not None else [None] * len(inputs)
    if len(range_list) != len(inputs):
        raise PDFMergeError("Number of page ranges must match number of files")

    output = Path(output)
    writer = PdfWriter()
    total = 0

    for path, spec in zip(inputs, range_list):
        path = Path(path)
        if not path.is_file():
            raise PDFMergeError(f"File not found: {path}")
        if path.resolve() == output.resolve():
            raise PDFMergeError("Output file cannot also be an input file")

        try:
            reader = PdfReader(str(path))
        except PdfReadError as exc:
            raise PDFMergeError(f"Could not read '{path.name}': {exc}") from exc

        if reader.is_encrypted:
            raise PDFMergeError(f"'{path.name}' is password-protected")

        first_page_index = total
        for index in parse_page_range(spec, len(reader.pages)):
            writer.add_page(reader.pages[index])
            total += 1

        if add_bookmarks and total > first_page_index:
            writer.add_outline_item(path.stem, first_page_index)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as f:
        writer.write(f)
    return total
