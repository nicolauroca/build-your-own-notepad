"""Application entrypoint and core logic for the notepad."""

from __future__ import annotations

import os
import sys
import tkinter as tk
import subprocess
from datetime import datetime
from tkinter import messagebox, simpledialog
from tkinter import font as tkfont

from . import file_ops
from .ui import NotepadUI


class Document:
    """Represents the state of a single document tab."""

    def __init__(self, tab_id: str, text_widget: tk.Text) -> None:
        self.tab_id = tab_id
        self.text = text_widget
        self.file_path: str | None = None
        self.dirty = False


class NotepadApp:
    """A minimal notepad-like text editor built with Tkinter."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Notepad")
        self.root.geometry("900x650")

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
            on_tab_change=self.on_tab_change,
        )

        self.documents: dict[str, Document] = {}
        self._add_blank_document()

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.update_title()
        self.update_status()

    def run(self) -> None:
        """Start the Tkinter main loop."""

        self.root.mainloop()

    def _add_blank_document(self, *, title: str = "Untitled") -> Document:
        """Create a new blank document tab and select it."""

        tab_id, text_widget = self.ui.add_tab(
            title, self.font, self.on_content_change, self.update_status
        )
        document = Document(tab_id, text_widget)
        self.documents[tab_id] = document
        self.ui.set_word_wrap(self.word_wrap)
        self.update_title()
        self.update_status()
        return document

    def _get_document_for_widget(self, widget: tk.Widget) -> Document | None:
        for document in self.documents.values():
            if document.text == widget:
                return document
        return None

    def _current_document(self) -> Document:
        tab_id, widget = self.ui.get_current_tab()
        if tab_id not in self.documents and widget:
            self.documents[tab_id] = Document(tab_id, widget)
        return self.documents[tab_id]

    def _select_document(self, document: Document) -> None:
        self.ui.select_tab(document.tab_id)

    def _document_display_name(self, document: Document) -> str:
        return os.path.basename(document.file_path) if document.file_path else "Untitled"

    def on_content_change(self, event=None) -> None:  # pragma: no cover - UI driven
        """Mark the active document as dirty when the user edits the text."""

        document = self._get_document_for_widget(event.widget) if event else self._current_document()
        if document and not document.dirty:
            document.dirty = True
            self.update_title()
        self.update_status(event)

    def on_tab_change(self, event=None) -> None:  # pragma: no cover - UI driven
        """Refresh window title and status bar when the user switches tabs."""

        self.update_title()
        self.update_status()

    def update_status(self, event=None) -> None:  # pragma: no cover - UI driven
        """Refresh status bar line/column information for the active tab."""

        document = self._get_document_for_widget(event.widget) if event else self._current_document()
        if not document:
            return

        index = document.text.index(tk.INSERT)
        line, column = (int(num) for num in index.split("."))
        self.ui.set_status(f"Ln {line}, Col {column + 1}")

    def new_file(self) -> None:  # pragma: no cover - UI driven
        """Create a blank document in a new tab."""

        self._add_blank_document()

    def new_window(self) -> None:  # pragma: no cover - UI driven
        """Open a new application window."""

        python_executable = sys.executable or "python"
        self.root.after(0, lambda: subprocess.Popen([python_executable, "main.py"], close_fds=True))

    def on_exit(self) -> None:  # pragma: no cover - UI driven
        """Prompt for unsaved changes before quitting."""

        for document in list(self.documents.values()):
            if not document.dirty:
                continue

            self._select_document(document)
            should_save = messagebox.askyesnocancel(
                "Unsaved Changes",
                f"You have unsaved changes in {self._document_display_name(document)}. Do you want to save before exiting?",
            )
            if should_save is None:
                return
            if should_save and not self.save_file(document):
                return

        self.root.destroy()

    def open_file(self) -> None:  # pragma: no cover - UI driven
        """Open a file, optionally prompting to save unsaved changes first."""

        content, file_path = file_ops.open_file()
        if file_path is None:
            return

        document = self._current_document()
        existing_text = document.text.get("1.0", "end-1c")
        if document.dirty or document.file_path or existing_text:
            document = self._add_blank_document(title=os.path.basename(file_path))

        document.text.delete("1.0", tk.END)
        document.text.insert(tk.END, content)
        document.file_path = file_path
        document.dirty = False
        self.update_title()

    def save_file(self, document: Document | None = None) -> bool:  # pragma: no cover - UI driven
        """Save the current buffer to disk."""

        document = document or self._current_document()
        content = document.text.get("1.0", "end-1c")
        file_path = file_ops.save_file(content, document.file_path)
        if file_path is None:
            return False

        document.file_path = file_path
        document.dirty = False
        self.update_title()
        return True

    def save_file_as(self) -> None:  # pragma: no cover - UI driven
        """Save the current buffer under a new file name."""

        document = self._current_document()
        content = document.text.get("1.0", "end-1c")
        file_path = file_ops.save_file_as(content)
        if file_path is None:
            return

        document.file_path = file_path
        document.dirty = False
        self.update_title()

    def undo(self) -> None:  # pragma: no cover - UI driven
        """Undo the last edit if possible."""

        document = self._current_document()
        try:
            document.text.edit_undo()
        except tk.TclError:
            return
        self.on_content_change()

    def redo(self) -> None:  # pragma: no cover - UI driven
        """Redo the last undone edit if possible."""

        document = self._current_document()
        try:
            document.text.edit_redo()
        except tk.TclError:
            return
        self.on_content_change()

    def cut(self) -> None:  # pragma: no cover - UI driven
        self.copy()
        self.delete_selection()

    def copy(self) -> None:  # pragma: no cover - UI driven
        document = self._current_document()
        try:
            selection = document.text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(selection)

    def paste(self) -> None:  # pragma: no cover - UI driven
        document = self._current_document()
        try:
            content = self.root.clipboard_get()
        except tk.TclError:
            return
        document.text.insert(tk.INSERT, content)
        self.on_content_change()

    def delete_selection(self) -> None:  # pragma: no cover - UI driven
        document = self._current_document()
        try:
            document.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return
        self.on_content_change()

    def select_all(self) -> None:  # pragma: no cover - UI driven
        document = self._current_document()
        document.text.tag_add(tk.SEL, "1.0", tk.END)
        document.text.mark_set(tk.INSERT, "1.0")
        document.text.see(tk.INSERT)

    def insert_time_date(self) -> None:  # pragma: no cover - UI driven
        document = self._current_document()
        document.text.insert(tk.INSERT, datetime.now().strftime("%H:%M %d/%m/%Y"))
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

        for document in self.documents.values():
            name = self._document_display_name(document)
            dirty_marker = " *" if document.dirty else ""
            self.ui.set_tab_title(document.tab_id, f"{name}{dirty_marker}")

        current_document = self._current_document()
        name = self._document_display_name(current_document)
        dirty_marker = " *" if current_document.dirty else ""
        self.root.title(f"{name}{dirty_marker} - Notepad")


def run() -> None:  # pragma: no cover - UI driven
    """Convenience wrapper to start the notepad application."""

    app = NotepadApp()
    app.run()
