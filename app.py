"""Web version of PDF Merger, built with Streamlit.

Run locally:
    streamlit run app.py
"""

import sys
import tempfile
from pathlib import Path

import streamlit as st

# Make the package in src/ importable without installing it
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_merger import PDFMergeError, merge_pdfs  # noqa: E402

st.set_page_config(page_title="PDF Merger", page_icon="📄", layout="centered")

st.title("📄 PDF Merger")
st.caption("Merge multiple PDF files into one. Files are processed in memory and not stored.")

uploaded = st.file_uploader(
    "Upload PDF files", type="pdf", accept_multiple_files=True
)

if uploaded:
    st.subheader("Order and pages")
    st.caption('Set the order number for each file. Pages: leave empty for all, or e.g. "1-3,5".')

    rows = []
    for i, file in enumerate(uploaded):
        col_name, col_order, col_pages = st.columns([3, 1, 2])
        col_name.markdown(f"**{file.name}**")
        order = col_order.number_input(
            "Order", min_value=1, value=i + 1, key=f"order_{i}", label_visibility="collapsed"
        )
        pages = col_pages.text_input(
            "Pages", key=f"pages_{i}", placeholder="all", label_visibility="collapsed"
        )
        rows.append((order, i, file, pages.strip() or None))

    bookmarks = st.checkbox("Add a bookmark for each file", value=True)
    output_name = st.text_input("Output file name", value="merged.pdf")
    if not output_name.lower().endswith(".pdf"):
        output_name += ".pdf"

    if st.button("Merge PDFs", type="primary", disabled=len(uploaded) < 2):
        rows.sort(key=lambda r: (r[0], r[1]))

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            paths, ranges = [], []
            for n, (_, _, file, pages) in enumerate(rows):
                # One folder per file so identical names don't overwrite each other,
                # while keeping the original name for the bookmark
                folder = tmp_dir / f"{n:02d}"
                folder.mkdir()
                path = folder / Path(file.name).name
                path.write_bytes(file.getvalue())
                paths.append(path)
                ranges.append(pages)

            out_path = tmp_dir / "merged_output.pdf"
            try:
                count = merge_pdfs(paths, out_path, ranges, add_bookmarks=bookmarks)
            except PDFMergeError as exc:
                st.error(str(exc))
            else:
                st.success(f"Done! {count} pages merged.")
                st.download_button(
                    "⬇️ Download merged PDF",
                    data=out_path.read_bytes(),
                    file_name=output_name,
                    mime="application/pdf",
                )

    if len(uploaded) < 2:
        st.info("Upload at least two PDF files to merge.")
