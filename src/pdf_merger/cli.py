"""Command-line interface.

Examples:
    pdf-merger a.pdf b.pdf -o merged.pdf
    pdf-merger a.pdf b.pdf -o merged.pdf --pages "1-3" all
    pdf-merger --gui
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from .core import PDFMergeError, merge_pdfs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdf-merger", description="Merge multiple PDF files into one."
    )
    parser.add_argument("files", nargs="*", help="PDF files to merge, in order")
    parser.add_argument("-o", "--output", default="merged.pdf", help="Output file")
    parser.add_argument(
        "-p",
        "--pages",
        nargs="*",
        help='Page range per file, e.g. "1-3,5" or "all" (one value per file)',
    )
    parser.add_argument(
        "--no-bookmarks", action="store_true", help="Don't add a bookmark per file"
    )
    parser.add_argument("--gui", action="store_true", help="Open the desktop app")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.gui or not args.files:
        from .gui import run_gui

        run_gui()
        return 0

    ranges = None
    if args.pages:
        ranges = [None if p.lower() == "all" else p for p in args.pages]

    try:
        count = merge_pdfs(
            args.files, args.output, ranges, add_bookmarks=not args.no_bookmarks
        )
    except PDFMergeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Done: {count} pages -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
