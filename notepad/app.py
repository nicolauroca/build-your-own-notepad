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
        self.language = "Plain Text"


class NotepadApp:
    """A minimal notepad-like text editor built with Tkinter."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Notepad")
        self.root.geometry("900x650")

        self.word_wrap = False
        self.toolbar_visible = True

        self.font = tkfont.Font(family="Arial", size=12)

        self.closed_documents: list[dict[str, str | None]] = []
        self.recent_files: list[str] = []
        self.last_search_query: str | None = None

        self.ui = NotepadUI(
            self.root,
            text_font=self.font,
            on_new=self.new_file,
            on_new_window=self.new_window,
            on_open=self.open_file,
            on_save=self.save_file,
            on_save_as=self.save_file_as,
            on_save_all=self.save_all,
            on_reload_file=self.reload_file,
            on_open_recent=self.open_recent,
            on_close_tab=self.close_current_tab,
            on_close_all=self.close_all_tabs,
            on_close_other_tabs=self.close_other_tabs,
            on_close_tabs_left=self.close_tabs_to_left,
            on_close_tabs_right=self.close_tabs_to_right,
            on_reopen_closed_tab=self.reopen_closed_tab,
            on_duplicate_tab=self.duplicate_tab,
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
            on_toggle_toolbar=self.toggle_toolbar,
            on_find=self.find,
            on_find_next=self.find_next,
            on_find_previous=self.find_previous,
            on_replace=self.replace,
            on_go_to=self.go_to,
            on_set_language=self.set_language,
            on_content_change=self.on_content_change,
            on_cursor_move=self.update_status,
            on_tab_change=self.on_tab_change,
        )

        self.documents: dict[str, Document] = {}
        self._add_blank_document()
        self.ui.update_recent_files(self.recent_files)

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
        self.ui.set_status(f"{document.language} | Ln {line}, Col {column + 1}")

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
        self._add_recent_file(file_path)
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
        self._add_recent_file(file_path)
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
        self._add_recent_file(file_path)
        self.update_title()

    def save_all(self) -> None:  # pragma: no cover - UI driven
        """Persist all open documents."""

        for document in list(self.documents.values()):
            self.save_file(document)

    def reload_file(self) -> None:  # pragma: no cover - UI driven
        """Reload the current file from disk if it has been saved before."""

        document = self._current_document()
        if not document.file_path:
            messagebox.showinfo("Reload", "Save the file before reloading from disk.")
            return

        try:
            with open(document.file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except OSError as exc:
            messagebox.showerror("Reload", f"Could not reload file:\n{exc}")
            return

        document.text.delete("1.0", tk.END)
        document.text.insert(tk.END, content)
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

    def toggle_toolbar(self) -> None:  # pragma: no cover - UI driven
        """Show or hide the quick access toolbar."""

        self.toolbar_visible = not self.toolbar_visible
        self.ui.toggle_toolbar(self.toolbar_visible)

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

    def find(self) -> None:  # pragma: no cover - UI driven
        """Prompt the user for a search term and highlight the first occurrence."""

        query = simpledialog.askstring("Find", "Enter text to find:", parent=self.root)
        if not query:
            return

        self.last_search_query = query
        self._select_search_result(query, direction="forward")

    def _select_search_result(self, query: str, *, direction: str) -> None:
        document = self._current_document()
        text = document.text
        start_index = text.index(tk.INSERT)
        search_start = start_index if direction == "forward" else f"{start_index} -1c"
        match_index = text.search(
            query,
            search_start,
            tk.END if direction == "forward" else "1.0",
            backwards=direction == "backward",
            nocase=False,
        )

        if not match_index:
            messagebox.showinfo("Find", "Text not found.")
            return

        end_index = f"{match_index}+{len(query)}c"
        text.tag_remove(tk.SEL, "1.0", tk.END)
        text.tag_add(tk.SEL, match_index, end_index)
        text.mark_set(tk.INSERT, end_index)
        text.see(match_index)
        self.update_status()

    def find_next(self) -> None:  # pragma: no cover - UI driven
        if not self.last_search_query:
            self.find()
            return

        self._select_search_result(self.last_search_query, direction="forward")

    def find_previous(self) -> None:  # pragma: no cover - UI driven
        if not self.last_search_query:
            self.find()
            return

        self._select_search_result(self.last_search_query, direction="backward")

    def replace(self) -> None:  # pragma: no cover - UI driven
        """Replace occurrences of a search term in the active document."""

        query = simpledialog.askstring("Replace", "Find what:", parent=self.root)
        if not query:
            return

        replacement = simpledialog.askstring("Replace", "Replace with:", parent=self.root)
        if replacement is None:
            return

        self.last_search_query = query
        document = self._current_document()
        content = document.text.get("1.0", tk.END)
        occurrences = content.count(query)
        if occurrences == 0:
            messagebox.showinfo("Replace", "No matches found.")
            return

        content = content.replace(query, replacement)
        document.text.delete("1.0", tk.END)
        document.text.insert("1.0", content)
        document.dirty = True
        messagebox.showinfo("Replace", f"Replaced {occurrences} occurrence(s).")
        self.update_status()

    def go_to(self) -> None:  # pragma: no cover - UI driven
        """Jump to a specific line number."""

        document = self._current_document()
        max_line = int(document.text.index("end-1c").split(".")[0])
        target = simpledialog.askinteger("Go To", "Line number:", minvalue=1, maxvalue=max_line)
        if not target:
            return

        document.text.mark_set(tk.INSERT, f"{target}.0")
        document.text.see(tk.INSERT)
        self.update_status()

    def set_language(self, language: str) -> None:  # pragma: no cover - UI driven
        """Label the current document with a language hint."""

        document = self._current_document()
        document.language = language
        self.update_status()
        self.update_title()

    def update_title(self) -> None:
        """Update the window title with the current filename and status."""

        for document in self.documents.values():
            name = self._document_display_name(document)
            dirty_marker = " *" if document.dirty else ""
            language_prefix = f"[{document.language}] " if document.language else ""
            self.ui.set_tab_title(document.tab_id, f"{language_prefix}{name}{dirty_marker}")

        current_document = self._current_document()
        name = self._document_display_name(current_document)
        dirty_marker = " *" if current_document.dirty else ""
        self.root.title(f"{name}{dirty_marker} - Notepad")

    def close_current_tab(self) -> None:  # pragma: no cover - UI driven
        self.close_document(self._current_document())

    def close_all_tabs(self) -> None:  # pragma: no cover - UI driven
        """Close all tabs after prompting for unsaved work."""

        for document in list(self.documents.values()):
            if not self.close_document(document):
                return

    def close_other_tabs(self) -> None:  # pragma: no cover - UI driven
        current = self._current_document()
        for document in list(self.documents.values()):
            if document.tab_id != current.tab_id:
                if not self.close_document(document):
                    return

    def _ordered_documents(self) -> list[Document]:
        ordered_ids = self.ui.tab_order()
        return [self.documents[tab_id] for tab_id in ordered_ids if tab_id in self.documents]

    def close_tabs_to_left(self) -> None:  # pragma: no cover - UI driven
        ordered = self._ordered_documents()
        current = self._current_document()
        for document in ordered:
            if document.tab_id == current.tab_id:
                break
            if not self.close_document(document):
                return

    def close_tabs_to_right(self) -> None:  # pragma: no cover - UI driven
        ordered = self._ordered_documents()
        current = self._current_document()
        found_current = False
        for document in ordered:
            if found_current and not self.close_document(document):
                return
            if document.tab_id == current.tab_id:
                found_current = True

    def duplicate_tab(self) -> None:  # pragma: no cover - UI driven
        """Clone the current document into a new unsaved tab."""

        document = self._current_document()
        clone = self._add_blank_document(title=self._document_display_name(document))
        content = document.text.get("1.0", "end-1c")
        clone.text.insert("1.0", content)
        clone.language = document.language
        clone.dirty = document.dirty
        self.update_title()

    def reopen_closed_tab(self) -> None:  # pragma: no cover - UI driven
        """Restore the most recently closed tab."""

        if not self.closed_documents:
            messagebox.showinfo("Reopen", "No recently closed tabs to reopen.")
            return

        state = self.closed_documents.pop()
        document = self._add_blank_document(title=state.get("title", "Untitled"))
        document.text.insert("1.0", state.get("content", ""))
        document.file_path = state.get("file_path")
        document.language = state.get("language", "Plain Text")
        document.dirty = False
        self.update_title()

    def close_document(self, document: Document) -> bool:  # pragma: no cover - UI driven
        """Close a document tab, prompting to save changes if needed."""

        if document.dirty:
            should_save = messagebox.askyesnocancel(
                "Unsaved Changes",
                f"You have unsaved changes in {self._document_display_name(document)}. Save before closing?",
            )
            if should_save is None:
                return False
            if should_save and not self.save_file(document):
                return False

        snapshot = {
            "title": self._document_display_name(document),
            "content": document.text.get("1.0", "end-1c"),
            "file_path": document.file_path,
            "language": document.language,
        }
        self.closed_documents.append(snapshot)

        self.ui.remove_tab(document.tab_id)
        self.documents.pop(document.tab_id, None)

        if not self.documents:
            self._add_blank_document()
        else:
            self.update_title()
            self.update_status()
        return True

    def _add_recent_file(self, file_path: str) -> None:
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]
        self.ui.update_recent_files(self.recent_files)

    def open_recent(self, file_path: str) -> None:  # pragma: no cover - UI driven
        """Open a file from the recent files list."""

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except OSError as exc:
            messagebox.showerror("Open Recent", f"Could not open file:\n{exc}")
            return

        document = self._add_blank_document(title=os.path.basename(file_path))
        document.text.insert("1.0", content)
        document.file_path = file_path
        document.dirty = False
        self._add_recent_file(file_path)
        self.update_title()


def run() -> None:  # pragma: no cover - UI driven
    """Convenience wrapper to start the notepad application."""

    app = NotepadApp()
    app.run()
