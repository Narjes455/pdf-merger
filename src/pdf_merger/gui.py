"""Simple Tkinter desktop app for merging PDFs."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .core import PDFMergeError, merge_pdfs


class MergerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PDF Merger")
        self.geometry("620x420")
        self.minsize(520, 360)
        self.files: list[str] = []
        self.bookmarks = tk.BooleanVar(value=True)
        self._build()

    def _build(self) -> None:
        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Files (in merge order):").pack(anchor="w")

        body = ttk.Frame(main)
        body.pack(fill="both", expand=True, pady=6)

        self.listbox = tk.Listbox(body, selectmode="extended")
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(body, command=self.listbox.yview)
        scroll.pack(side="left", fill="y")
        self.listbox.config(yscrollcommand=scroll.set)

        buttons = ttk.Frame(body, padding=(8, 0))
        buttons.pack(side="left", fill="y")
        for text, cmd in [
            ("Add files…", self.add_files),
            ("Remove", self.remove_selected),
            ("Move up", lambda: self.move(-1)),
            ("Move down", lambda: self.move(1)),
            ("Clear", self.clear),
        ]:
            ttk.Button(buttons, text=text, command=cmd).pack(fill="x", pady=2)

        bottom = ttk.Frame(main)
        bottom.pack(fill="x")
        ttk.Checkbutton(
            bottom, text="Add a bookmark for each file", variable=self.bookmarks
        ).pack(side="left")
        ttk.Button(bottom, text="Merge PDFs", command=self.merge).pack(side="right")

        self.status = ttk.Label(main, text="Add at least two PDF files.")
        self.status.pack(anchor="w", pady=(8, 0))

    def refresh(self) -> None:
        self.listbox.delete(0, "end")
        for f in self.files:
            self.listbox.insert("end", Path(f).name)
        self.status.config(text=f"{len(self.files)} file(s) selected")

    def add_files(self) -> None:
        paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        self.files.extend(p for p in paths if p not in self.files)
        self.refresh()

    def remove_selected(self) -> None:
        for i in reversed(self.listbox.curselection()):
            del self.files[i]
        self.refresh()

    def move(self, step: int) -> None:
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        i, j = sel[0], sel[0] + step
        if 0 <= j < len(self.files):
            self.files[i], self.files[j] = self.files[j], self.files[i]
            self.refresh()
            self.listbox.selection_set(j)

    def clear(self) -> None:
        self.files.clear()
        self.refresh()

    def merge(self) -> None:
        if len(self.files) < 2:
            messagebox.showwarning("PDF Merger", "Please add at least two PDF files.")
            return
        out = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile="merged.pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not out:
            return
        try:
            count = merge_pdfs(self.files, out, add_bookmarks=self.bookmarks.get())
        except PDFMergeError as exc:
            messagebox.showerror("PDF Merger", str(exc))
            return
        self.status.config(text=f"Saved {count} pages to {Path(out).name}")
        messagebox.showinfo("PDF Merger", f"Done! {count} pages merged.")


def run_gui() -> None:
    MergerApp().mainloop()
