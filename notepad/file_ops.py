"""File operation helpers for the notepad application."""

from __future__ import annotations

from tkinter import filedialog, messagebox


def open_file() -> tuple[str | None, str | None]:
    """
    Ask the user to choose a file to open and return its contents and path.

    Returns
    -------
    tuple[str | None, str | None]
        A pair containing the file content and the selected path. Both
        values are ``None`` if the user cancels the dialog or an error occurs.
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
        return None, None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except OSError as exc:  # pragma: no cover - UI interaction is manual
        messagebox.showerror("Open File", f"Could not open file:\n{exc}")
        return None, None

    return content, file_path


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
