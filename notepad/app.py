"""Application entrypoint and core logic for the notepad."""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox

from . import file_ops
from .ui import NotepadUI


class NotepadApp:
    """A minimal notepad-like text editor built with Tkinter."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Notepad")
        self.root.geometry("800x600")

        self.file_path: str | None = None
        self.dirty = False

        self.ui = NotepadUI(
            self.root,
            on_open=self.open_file,
            on_save=self.save_file,
            on_save_as=self.save_file_as,
            on_exit=self.on_exit,
            on_content_change=self.on_content_change,
        )

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.update_title()

    def run(self) -> None:
        """Start the Tkinter main loop."""

        self.root.mainloop()

    def on_content_change(self, event=None) -> None:  # pragma: no cover - UI driven
        """Mark the document as dirty when the user edits the text."""

        if not self.dirty:
            self.dirty = True
            self.update_title()

    def on_exit(self) -> None:  # pragma: no cover - UI driven
        """Prompt for unsaved changes before quitting."""

        if self.dirty:
            should_save = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
            )
            if should_save is None:
                return
            if should_save and not self.save_file():
                return

        self.root.destroy()

    def open_file(self) -> None:  # pragma: no cover - UI driven
        """Open a file, optionally prompting to save unsaved changes first."""

        if self.dirty:
            should_save = messagebox.askyesnocancel(
                "Unsaved Changes", "Save current file before opening another?"
            )
            if should_save is None:
                return
            if should_save and not self.save_file():
                return

        content, file_path = file_ops.open_file()
        if file_path is None:
            return

        self.ui.text.delete("1.0", tk.END)
        self.ui.text.insert(tk.END, content)
        self.file_path = file_path
        self.dirty = False
        self.update_title()

    def save_file(self) -> bool:  # pragma: no cover - UI driven
        """Save the current buffer to disk."""

        content = self.ui.text.get("1.0", "end-1c")
        file_path = file_ops.save_file(content, self.file_path)
        if file_path is None:
            return False

        self.file_path = file_path
        self.dirty = False
        self.update_title()
        return True

    def save_file_as(self) -> None:  # pragma: no cover - UI driven
        """Save the current buffer under a new file name."""

        content = self.ui.text.get("1.0", "end-1c")
        file_path = file_ops.save_file_as(content)
        if file_path is None:
            return

        self.file_path = file_path
        self.dirty = False
        self.update_title()

    def update_title(self) -> None:
        """Update the window title with the current filename and status."""

        name = os.path.basename(self.file_path) if self.file_path else "Untitled"
        dirty_marker = " *" if self.dirty else ""
        self.root.title(f"{name}{dirty_marker} - Notepad")


def run() -> None:  # pragma: no cover - UI driven
    """Convenience wrapper to start the notepad application."""

    app = NotepadApp()
    app.run()
