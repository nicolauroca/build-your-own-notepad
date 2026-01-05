"""Application entrypoint and core logic for the notepad."""

from __future__ import annotations

import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog
from tkinter import font as tkfont

from . import file_ops
from .ui import NotepadUI


class NotepadApp:
    """A minimal notepad-like text editor built with Tkinter."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Notepad")
        self.root.geometry("900x650")

        self.file_path: str | None = None
        self.dirty = False
        self.word_wrap = False

        self.font = tkfont.Font(family="Arial", size=12)

        self.ui = NotepadUI(
            self.root,
            text_font=self.font,
            on_new=self.new_file,
            on_new_window=self.new_window,
            on_open=self.open_file,
            on_save=self.save_file,
            on_save_as=self.save_file_as,
            on_exit=self.on_exit,
            on_undo=self.undo,
            on_redo=self.redo,
            on_cut=self.cut,
            on_copy=self.copy,
            on_paste=self.paste,
            on_delete=self.delete_selection,
            on_select_all=self.select_all,
            on_time_date=self.insert_time_date,
            on_word_wrap=self.toggle_word_wrap,
            on_choose_font=self.choose_font,
            on_zoom_in=self.zoom_in,
            on_zoom_out=self.zoom_out,
            on_zoom_reset=self.zoom_reset,
            on_toggle_status_bar=self.toggle_status_bar,
            on_content_change=self.on_content_change,
            on_cursor_move=self.update_status,
        )

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.update_title()
        self.update_status()

    def run(self) -> None:
        """Start the Tkinter main loop."""

        self.root.mainloop()

    def on_content_change(self, event=None) -> None:  # pragma: no cover - UI driven
        """Mark the document as dirty when the user edits the text."""

        if not self.dirty:
            self.dirty = True
            self.update_title()
        self.update_status()

    def update_status(self, event=None) -> None:  # pragma: no cover - UI driven
        """Refresh status bar line/column information."""

        index = self.ui.text.index(tk.INSERT)
        line, column = (int(num) for num in index.split("."))
        self.ui.set_status(f"Ln {line}, Col {column + 1}")

    def new_file(self) -> None:  # pragma: no cover - UI driven
        """Create a blank document, prompting to save changes if needed."""

        if not self._confirm_discard_changes("create a new file"):
            return

        self.ui.text.delete("1.0", tk.END)
        self.file_path = None
        self.dirty = False
        self.update_title()
        self.update_status()

    def new_window(self) -> None:  # pragma: no cover - UI driven
        """Open a new application window."""

        python_executable = sys.executable or "python"
        self.root.after(0, lambda: os.spawnlp(os.P_NOWAIT, python_executable, python_executable, "main.py"))

    def _confirm_discard_changes(self, action_description: str) -> bool:
        """Ask the user whether to save before continuing with the action."""

        if not self.dirty:
            return True

        should_save = messagebox.askyesnocancel(
            "Unsaved Changes",
            f"You have unsaved changes. Save before {action_description}?",
        )
        if should_save is None:
            return False
        if should_save:
            return self.save_file()
        return True

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

        if not self._confirm_discard_changes("opening another file"):
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

    def undo(self) -> None:  # pragma: no cover - UI driven
        """Undo the last edit if possible."""

        try:
            self.ui.text.edit_undo()
        except tk.TclError:
            return
        self.on_content_change()

    def redo(self) -> None:  # pragma: no cover - UI driven
        """Redo the last undone edit if possible."""

        try:
            self.ui.text.edit_redo()
        except tk.TclError:
            return
        self.on_content_change()

    def cut(self) -> None:  # pragma: no cover - UI driven
        self.copy()
        self.delete_selection()

    def copy(self) -> None:  # pragma: no cover - UI driven
        try:
            selection = self.ui.text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(selection)

    def paste(self) -> None:  # pragma: no cover - UI driven
        try:
            content = self.root.clipboard_get()
        except tk.TclError:
            return
        self.ui.text.insert(tk.INSERT, content)
        self.on_content_change()

    def delete_selection(self) -> None:  # pragma: no cover - UI driven
        try:
            self.ui.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return
        self.on_content_change()

    def select_all(self) -> None:  # pragma: no cover - UI driven
        self.ui.text.tag_add(tk.SEL, "1.0", tk.END)
        self.ui.text.mark_set(tk.INSERT, "1.0")
        self.ui.text.see(tk.INSERT)

    def insert_time_date(self) -> None:  # pragma: no cover - UI driven
        self.ui.text.insert(tk.INSERT, datetime.now().strftime("%H:%M %d/%m/%Y"))
        self.on_content_change()

    def toggle_word_wrap(self) -> None:  # pragma: no cover - UI driven
        self.word_wrap = not self.word_wrap
        self.ui.set_word_wrap(self.word_wrap)

    def choose_font(self) -> None:  # pragma: no cover - UI driven
        current_family = self.font.actual().get("family", "Arial")
        current_size = self.font.actual().get("size", 12)

        family = simpledialog.askstring(
            "Font Family", "Enter font family (e.g., Arial, Courier New):", initialvalue=current_family
        )
        if not family:
            return

        size = simpledialog.askinteger(
            "Font Size", "Enter font size:", initialvalue=current_size, minvalue=6, maxvalue=96
        )
        if not size:
            return

        self.font.config(family=family, size=size)
        self.update_status()

    def zoom_in(self) -> None:  # pragma: no cover - UI driven
        self.font.config(size=self.font.cget("size") + 1)
        self.update_status()

    def zoom_out(self) -> None:  # pragma: no cover - UI driven
        self.font.config(size=max(6, self.font.cget("size") - 1))
        self.update_status()

    def zoom_reset(self) -> None:  # pragma: no cover - UI driven
        self.font.config(size=12)
        self.update_status()

    def toggle_status_bar(self) -> None:  # pragma: no cover - UI driven
        self.ui.toggle_status_bar()

    def update_title(self) -> None:
        """Update the window title with the current filename and status."""

        name = os.path.basename(self.file_path) if self.file_path else "Untitled"
        dirty_marker = " *" if self.dirty else ""
        self.root.title(f"{name}{dirty_marker} - Notepad")


def run() -> None:  # pragma: no cover - UI driven
    """Convenience wrapper to start the notepad application."""

    app = NotepadApp()
    app.run()
