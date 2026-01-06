"""File operation helpers for the notepad application."""

from __future__ import annotations

import codecs

from tkinter import filedialog, messagebox


def _detect_encoding(raw_bytes: bytes) -> tuple[str, str]:
    """Infer a file's encoding label and Python codec from its byte content."""

    if raw_bytes.startswith(codecs.BOM_UTF8):
        return "UTF-8-BOM", "utf-8-sig"
    if raw_bytes.startswith(codecs.BOM_UTF16_LE):
        return "UTF-16 LE", "utf-16-le"
    if raw_bytes.startswith(codecs.BOM_UTF16_BE):
        return "UTF-16 BE", "utf-16-be"

    try:
        raw_bytes.decode("utf-8")
        return "UTF-8", "utf-8"
    except UnicodeDecodeError:
        return "ANSI", "cp1252"


def read_file_with_encoding(file_path: str) -> tuple[str | None, str | None]:
    """Load ``file_path`` returning both content and detected encoding label."""

    try:
        with open(file_path, "rb") as file:
            raw = file.read()
    except OSError as exc:  # pragma: no cover - UI interaction is manual
        messagebox.showerror("Open File", f"Could not open file:\n{exc}")
        return None, None

    label, codec = _detect_encoding(raw)
    try:
        content = raw.decode(codec)
    except UnicodeDecodeError:
        messagebox.showerror(
            "Open File", f"File contents are not compatible with detected encoding ({label})."
        )
        return None, None

    return content, label


def open_file() -> tuple[str | None, str | None, str | None]:
    """
    Ask the user to choose a file to open and return its contents, path, and encoding.

    Returns
    -------
    tuple[str | None, str | None, str | None]
        The file content, the selected path, and the detected encoding label.
        All values are ``None`` if the user cancels the dialog or an error occurs.
    """

    file_path = filedialog.askopenfilename(
        title="Open File",
        filetypes=(
            ("Text Files", "*.txt"),
            ("Python Files", "*.py"),
            ("All Files", "*.*"),
        ),
    )

    if not file_path:
        return None, None, None

    content, encoding = read_file_with_encoding(file_path)
    if content is None:
        return None, None, None

    return content, file_path, encoding


def save_file(content: str, file_path: str | None, *, encoding: str = "utf-8") -> str | None:
    """
    Save ``content`` to ``file_path`` if provided, otherwise prompt the user.

    Parameters
    ----------
    content:
        Text to persist to disk.
    file_path:
        Destination path or ``None`` to trigger the Save As dialog.

    Returns
    -------
    str | None
        The path the content was saved to, or ``None`` if the user cancels or
        an error occurs.
    """

    if not file_path:
        return save_file_as(content)

    try:
        with open(file_path, "w", encoding=encoding) as file:
            file.write(content)
    except OSError as exc:  # pragma: no cover - UI interaction is manual
        messagebox.showerror("Save File", f"Could not save file:\n{exc}")
        return None

    return file_path


def save_file_as(content: str, *, encoding: str = "utf-8") -> str | None:
    """Prompt the user for a path and save ``content`` to that location."""

    file_path = filedialog.asksaveasfilename(
        title="Save File As",
        defaultextension=".txt",
        filetypes=(
            ("Text Files", "*.txt"),
            ("Python Files", "*.py"),
            ("All Files", "*.*"),
        ),
    )

    if not file_path:
        return None

    try:
        with open(file_path, "w", encoding=encoding) as file:
            file.write(content)
    except OSError as exc:  # pragma: no cover - UI interaction is manual
        messagebox.showerror("Save File", f"Could not save file:\n{exc}")
        return None

    return file_path
