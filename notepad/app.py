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
        self.encoding = "UTF-8"


class NotepadApp:
    """A minimal notepad-like text editor built with Tkinter."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Notepad")
        self.root.geometry("900x650")

        self.word_wrap = False
        self.toolbar_visible = True

        self.font = self._select_editor_font()

        self.closed_documents: list[dict[str, str | None]] = []
        self.recent_files: list[str] = []
        self.last_search_query: str | None = None
        self.command_actions: list[dict[str, object]] = []

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
            on_set_encoding=self.set_encoding,
            on_convert_encoding=self.convert_encoding,
            on_content_change=self.on_content_change,
            on_cursor_move=self.update_status,
            on_tab_change=self.on_tab_change,
            on_open_command_palette=self.open_command_palette,
        )

        self.documents: dict[str, Document] = {}
        self._add_blank_document()
        self.ui.update_recent_files(self.recent_files)
        self._register_command_actions()
        self.ui.update_commands_menu(self.command_actions)

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
        self.ui.set_selected_encoding(document.encoding)
        self.update_title()
        self.update_status()
        return document

    def _select_editor_font(self) -> tkfont.Font:
        """Pick a modern, developer-friendly font with fallbacks."""

        preferred = (
            "JetBrains Mono",
            "Cascadia Code",
            "Fira Code",
            "IBM Plex Mono",
            "Menlo",
            "Consolas",
            "SF Mono",
        )
        available = set(tkfont.families())
        for family in preferred:
            if family in available:
                return tkfont.Font(family=family, size=13)

        return tkfont.Font(family="Courier New", size=12)

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
        self.ui.set_selected_encoding(document.encoding)
        self.ui.set_status(f"{document.encoding} | Ln {line}, Col {column + 1}")

    # Command palette helpers
    def _register_command(self, name: str, action, icon: str) -> None:
        self.command_actions.append({"name": name, "action": action, "icon": icon})

    def _register_command_actions(self) -> None:
        self.command_actions.clear()
        self._register_command("Uppercase selection", self.uppercase_selection, "🔠")
        self._register_command("Lowercase selection", self.lowercase_selection, "🔡")
        self._register_command("Title Case selection", self.title_case_selection, "🔤")
        self._register_command("Sentence case selection", self.sentence_case_selection, "✒️")
        self._register_command("Swap case", self.swap_case_selection, "🔄")
        self._register_command("Trim trailing whitespace", self.trim_trailing_whitespace, "✂️")
        self._register_command("Trim leading whitespace", self.trim_leading_whitespace, "🧹")
        self._register_command("Trim surrounding whitespace", self.trim_borders, "🪄")
        self._register_command("Convert tabs to spaces", self.convert_tabs_to_spaces, "↔️")
        self._register_command("Convert spaces to tabs", self.convert_spaces_to_tabs, "↕️")
        self._register_command("Indent with 2 spaces", self.indent_with_two_spaces, "↪️")
        self._register_command("Indent with 4 spaces", self.indent_with_four_spaces, "⤵️")
        self._register_command("Toggle comment", self.toggle_comment, "💬")
        self._register_command("Comment selection", self.comment_selection, "🗣️")
        self._register_command("Uncomment selection", self.uncomment_selection, "🔇")
        self._register_command("Duplicate line/selection", self.duplicate_selection_or_line, "📑")
        self._register_command("Duplicate above", self.duplicate_above, "⬆️")
        self._register_command("Duplicate below", self.duplicate_below, "⬇️")
        self._register_command("Delete current line", self.delete_line, "🗑️")
        self._register_command("Move line up", self.move_line_up, "🔼")
        self._register_command("Move line down", self.move_line_down, "🔽")
        self._register_command("Join lines", self.join_lines, "📎")
        self._register_command("Split selection by commas", self.split_lines_by_commas, "🍴")
        self._register_command("Sort lines ascending", self.sort_lines_ascending, "⬆")
        self._register_command("Sort lines descending", self.sort_lines_descending, "⬇")
        self._register_command("Reverse lines", self.reverse_lines, "🔁")
        self._register_command("Unique lines", self.unique_lines, "✅")
        self._register_command("Remove blank lines", self.remove_blank_lines, "🚫")
        self._register_command("Wrap with ( )", self.wrap_with_parentheses, "( )")
        self._register_command("Wrap with [ ]", self.wrap_with_brackets, "[ ]")
        self._register_command("Wrap with { }", self.wrap_with_braces, "{ }")
        self._register_command("Wrap with single quotes", self.wrap_with_single_quotes, "' '")
        self._register_command("Wrap with double quotes", self.wrap_with_double_quotes, '" "')
        self._register_command("Wrap with backticks", self.wrap_with_backticks, "` `")
        self._register_command("Convert to snake_case", self.to_snake_case, "🐍")
        self._register_command("Convert to camelCase", self.to_camel_case, "🐪")
        self._register_command("Convert to PascalCase", self.to_pascal_case, "🅿️")
        self._register_command("Convert to kebab-case", self.to_kebab_case, "🥙")
        self._register_command("Convert to UPPER_SNAKE", self.to_upper_snake_case, "🔺")
        self._register_command("Insert TODO comment", self.insert_todo_comment, "✅")
        self._register_command("Insert ISO timestamp", self.insert_iso_timestamp, "⏱️")
        self._register_command("Add line numbers", self.add_line_numbers, "🔢")
        self._register_command("Remove line numbers", self.remove_line_numbers, "🚮")
        self._register_command("Align assignments", self.align_assignments, "📐")
        self._register_command("Toggle bullet list", self.toggle_bullet_list, "•")
        self._register_command("Toggle numbered list", self.toggle_numbered_list, "1️⃣")
        self._register_command("Transpose characters", self.transpose_characters, "🔀")
        self._register_command("Select current line", self.select_current_line, "📍")
        self._register_command("Select word", self.select_word, "🪄")
        self._register_command("Go to matching bracket", self.go_to_matching_bracket, "📏")
        self._register_command("Sort by line length", self.sort_by_line_length, "📏")
        self._register_command("Collapse multiple spaces", self.collapse_spaces, "🧽")
        self._register_command("Pad numbers with zeros", self.pad_numbers, "0️⃣")
        self._register_command("Strip BOM", self.strip_bom, "🧽")
        self._register_command("Convert quotes to double", self.normalize_double_quotes, "💬")
        self._register_command("Convert quotes to single", self.normalize_single_quotes, "🗨️")

    def _encoding_codec(self, label: str) -> str:
        codecs = {
            "UTF-8": "utf-8",
            "UTF-8-BOM": "utf-8-sig",
            "UTF-16 LE": "utf-16-le",
            "UTF-16 BE": "utf-16-be",
            "ANSI": "cp1252",
        }
        return codecs.get(label, "utf-8")

    def open_command_palette(self) -> None:  # pragma: no cover - UI driven
        palette = tk.Toplevel(self.root)
        palette.title("Command Palette")
        palette.geometry("440x520")
        palette.transient(self.root)
        palette.grab_set()

        tk.Label(palette, text="Scope:").pack(anchor=tk.W, padx=10, pady=(10, 2))
        scope_var = tk.StringVar(value="active")
        scope_frame = tk.Frame(palette)
        scope_frame.pack(fill=tk.X, padx=10)
        tk.Radiobutton(scope_frame, text="Selected text", variable=scope_var, value="selection").pack(
            side=tk.LEFT, padx=4
        )
        tk.Radiobutton(scope_frame, text="Active document", variable=scope_var, value="active").pack(
            side=tk.LEFT, padx=4
        )
        tk.Radiobutton(scope_frame, text="All tabs", variable=scope_var, value="all").pack(
            side=tk.LEFT, padx=4
        )

        tk.Label(palette, text="Search command:").pack(anchor=tk.W, padx=10, pady=(8, 2))
        query_var = tk.StringVar()
        entry = tk.Entry(palette, textvariable=query_var)
        entry.pack(fill=tk.X, padx=10)

        scrollbar = tk.Scrollbar(palette)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = tk.Listbox(palette, yscrollcommand=scrollbar.set)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=listbox.yview)

        def refresh_list(*_):
            query = query_var.get().lower()
            listbox.delete(0, tk.END)
            for command in self.command_actions:
                label = f"{command['icon']} {command['name']}"
                if query in command["name"].lower():
                    listbox.insert(tk.END, label)
            if listbox.size():
                listbox.selection_set(0)

        def run_selected(event=None):
            if not listbox.size():
                return
            selection = listbox.get(listbox.curselection())
            for command in self.command_actions:
                label = f"{command['icon']} {command['name']}"
                if label == selection:
                    if self._run_command_with_scope(command["action"], scope_var.get()):
                        palette.destroy()
                    break

        entry.bind("<KeyRelease>", refresh_list)
        listbox.bind("<Double-Button-1>", run_selected)
        listbox.bind("<Return>", run_selected)
        entry.focus_set()
        refresh_list()
        palette.wait_window()

    def _run_command_with_scope(self, action, scope: str) -> bool:
        if scope == "selection":
            document = self._current_document()
            if not self._selection_range(document.text):
                messagebox.showinfo("Command Palette", "Seleccione texto para usar esta acción.")
                return False
            action()
            return True

        if scope == "all":
            current_tab, _widget = self.ui.get_current_tab()
            for tab_id in self.ui.tab_order():
                self.ui.select_tab(tab_id)
                action()
            self.ui.select_tab(current_tab)
            self.update_status()
            return True

        action()
        return True


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

        content, file_path, encoding = file_ops.open_file()
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
        document.encoding = encoding or "UTF-8"
        self._add_recent_file(file_path)
        self.update_title()
        self.update_status()

    def save_file(self, document: Document | None = None) -> bool:  # pragma: no cover - UI driven
        """Save the current buffer to disk."""

        document = document or self._current_document()
        content = document.text.get("1.0", "end-1c")
        file_path = file_ops.save_file(
            content, document.file_path, encoding=self._encoding_codec(document.encoding)
        )
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
        file_path = file_ops.save_file_as(content, encoding=self._encoding_codec(document.encoding))
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
            with open(document.file_path, "r", encoding=self._encoding_codec(document.encoding)) as file:
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
        current_family = self.font.actual().get("family", "Consolas")
        current_size = self.font.actual().get("size", 12)
        selection = self.ui.prompt_for_font_choice(current_family, current_size)
        if not selection:
            return
        family, size = selection
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

    def set_encoding(self, label: str) -> None:  # pragma: no cover - UI driven
        """Update the encoding metadata for the active document."""

        document = self._current_document()
        document.encoding = label
        self.ui.set_selected_encoding(label)
        self.update_status()
        self.update_title()

    def convert_encoding(self, label: str) -> None:  # pragma: no cover - UI driven
        """Transcode the document content and persist the chosen encoding."""

        document = self._current_document()
        target_codec = self._encoding_codec(label)
        content = document.text.get("1.0", "end-1c")
        try:
            converted = content.encode(target_codec, errors="strict").decode(target_codec)
        except UnicodeError:
            messagebox.showerror(
                "Encoding",
                f"Content contains characters incompatible with {label}.",
            )
            return

        document.text.delete("1.0", tk.END)
        document.text.insert("1.0", converted)
        document.encoding = label
        document.dirty = True
        self.ui.set_selected_encoding(label)
        self.update_status()
        self.update_title()

    def update_title(self) -> None:
        """Update the window title with the current filename and status."""

        for document in self.documents.values():
            name = self._document_display_name(document)
            dirty_marker = " *" if document.dirty else ""
            encoding_prefix = f"[{document.encoding}] " if document.encoding else ""
            self.ui.set_tab_title(document.tab_id, f"{encoding_prefix}{name}{dirty_marker}")

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
        clone.encoding = document.encoding
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
        document.encoding = state.get("encoding", "UTF-8")
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
            "encoding": document.encoding,
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

        content, encoding = file_ops.read_file_with_encoding(file_path)
        if content is None:
            return

        document = self._add_blank_document(title=os.path.basename(file_path))
        document.text.insert("1.0", content)
        document.file_path = file_path
        document.dirty = False
        document.encoding = encoding or "UTF-8"
        self._add_recent_file(file_path)
        self.update_title()
        self.update_status()

    # ----- Advanced editing helpers -----
    def _active_text(self) -> tk.Text:
        return self._current_document().text

    def _selection_range(self, text: tk.Text) -> tuple[str, str] | None:
        try:
            return text.index(tk.SEL_FIRST), text.index(tk.SEL_LAST)
        except tk.TclError:
            return None

    def _apply_transform(self, transform, *, default_to_document: bool = True) -> None:
        document = self._current_document()
        text = document.text
        selection = self._selection_range(text)
        if selection:
            start, end = selection
        elif default_to_document:
            start, end = "1.0", "end-1c"
        else:
            line = text.index("insert linestart"), text.index("insert lineend")
            start, end = line

        snippet = text.get(start, end)
        text.delete(start, end)
        text.insert(start, transform(snippet))
        document.dirty = True
        self.update_title()
        self.update_status()

    def uppercase_selection(self) -> None:
        self._apply_transform(lambda s: s.upper())

    def lowercase_selection(self) -> None:
        self._apply_transform(lambda s: s.lower())

    def title_case_selection(self) -> None:
        self._apply_transform(lambda s: s.title())

    def sentence_case_selection(self) -> None:
        def _sentence(text: str) -> str:
            parts = text.split(".")
            return ".".join(p.strip().capitalize() if p.strip() else "" for p in parts)

        self._apply_transform(_sentence)

    def swap_case_selection(self) -> None:
        self._apply_transform(lambda s: s.swapcase())

    def trim_trailing_whitespace(self) -> None:
        self._apply_transform(lambda s: "\n".join(line.rstrip() for line in s.splitlines()))

    def trim_leading_whitespace(self) -> None:
        self._apply_transform(lambda s: "\n".join(line.lstrip() for line in s.splitlines()))

    def trim_borders(self) -> None:
        self._apply_transform(lambda s: "\n".join(line.strip() for line in s.splitlines()))

    def convert_tabs_to_spaces(self) -> None:
        self._apply_transform(lambda s: s.replace("\t", "    "))

    def convert_spaces_to_tabs(self) -> None:
        self._apply_transform(lambda s: s.replace("    ", "\t"))

    def indent_with_two_spaces(self) -> None:
        self._apply_transform(lambda s: "\n".join("  " + line.lstrip() for line in s.splitlines()))

    def indent_with_four_spaces(self) -> None:
        self._apply_transform(lambda s: "\n".join("    " + line.lstrip() for line in s.splitlines()))

    def toggle_comment(self) -> None:
        document = self._current_document()
        text = document.text
        selection = self._selection_range(text)
        if not selection:
            start, end = text.index("insert linestart"), text.index("insert lineend")
        else:
            start, end = selection
        lines = text.get(start, end).splitlines()
        if all(line.strip().startswith("#") for line in lines if line.strip()):
            new_lines = [line.replace("#", "", 1) if line.strip().startswith("#") else line for line in lines]
        else:
            new_lines = [f"# {line}" if line.strip() else line for line in lines]
        text.delete(start, end)
        text.insert(start, "\n".join(new_lines))
        document.dirty = True
        self.update_title()

    def comment_selection(self) -> None:
        self._apply_transform(lambda s: "\n".join(f"# {line}" if line.strip() else line for line in s.splitlines()))

    def uncomment_selection(self) -> None:
        self._apply_transform(lambda s: "\n".join(line[1:].lstrip() if line.strip().startswith("#") else line for line in s.splitlines()))

    def duplicate_selection_or_line(self) -> None:
        document = self._current_document()
        text = document.text
        selection = self._selection_range(text)
        if selection:
            start, end = selection
        else:
            start, end = text.index("insert linestart"), text.index("insert lineend+1c")
        content = text.get(start, end)
        text.insert(end, content)
        document.dirty = True
        self.update_title()

    def duplicate_above(self) -> None:
        document = self._current_document()
        text = document.text
        line_start = text.index("insert linestart")
        line_end = text.index("insert lineend+1c")
        content = text.get(line_start, line_end)
        text.insert(line_start, content)
        document.dirty = True
        self.update_title()

    def duplicate_below(self) -> None:
        document = self._current_document()
        text = document.text
        line_start = text.index("insert linestart")
        line_end = text.index("insert lineend+1c")
        content = text.get(line_start, line_end)
        text.insert(line_end, content)
        document.dirty = True
        self.update_title()

    def delete_line(self) -> None:
        document = self._current_document()
        text = document.text
        start, end = text.index("insert linestart"), text.index("insert lineend+1c")
        text.delete(start, end)
        document.dirty = True
        self.update_title()

    def move_line_up(self) -> None:
        self._move_line(-1)

    def move_line_down(self) -> None:
        self._move_line(1)

    def _move_line(self, direction: int) -> None:
        document = self._current_document()
        text = document.text
        current_line = int(text.index("insert").split(".")[0])
        target_line = current_line + direction
        if target_line < 1:
            return
        line_start = f"{current_line}.0"
        line_end = f"{current_line}.0 lineend+1c"
        content = text.get(line_start, line_end)
        text.delete(line_start, line_end)
        text.insert(f"{target_line}.0", content)
        document.dirty = True
        self.update_title()

    def join_lines(self) -> None:
        self._apply_transform(lambda s: " ".join(line.strip() for line in s.splitlines()))

    def split_lines_by_commas(self) -> None:
        self._apply_transform(lambda s: "\n".join(part.strip() for part in s.split(",")))

    def sort_lines_ascending(self) -> None:
        self._apply_transform(lambda s: "\n".join(sorted(s.splitlines())))

    def sort_lines_descending(self) -> None:
        self._apply_transform(lambda s: "\n".join(sorted(s.splitlines(), reverse=True)))

    def sort_by_line_length(self) -> None:
        self._apply_transform(lambda s: "\n".join(sorted(s.splitlines(), key=len)))

    def reverse_lines(self) -> None:
        self._apply_transform(lambda s: "\n".join(reversed(s.splitlines())))

    def unique_lines(self) -> None:
        def _unique(text: str) -> str:
            seen = set()
            output = []
            for line in text.splitlines():
                if line not in seen:
                    output.append(line)
                    seen.add(line)
            return "\n".join(output)

        self._apply_transform(_unique)

    def remove_blank_lines(self) -> None:
        self._apply_transform(lambda s: "\n".join(line for line in s.splitlines() if line.strip()))

    def wrap_with_parentheses(self) -> None:
        self._apply_transform(lambda s: f"({s})")

    def wrap_with_brackets(self) -> None:
        self._apply_transform(lambda s: f"[{s}]")

    def wrap_with_braces(self) -> None:
        self._apply_transform(lambda s: f"{{{s}}}")

    def wrap_with_single_quotes(self) -> None:
        self._apply_transform(lambda s: f"'{s}'")

    def wrap_with_double_quotes(self) -> None:
        self._apply_transform(lambda s: f'"{s}"')

    def wrap_with_backticks(self) -> None:
        self._apply_transform(lambda s: f"`{s}`")

    def _normalize_words(self, text: str) -> list[str]:
        return [word for word in text.replace("-", " ").replace("_", " ").split() if word]

    def to_snake_case(self) -> None:
        self._apply_transform(lambda s: "_".join(self._normalize_words(s)).lower())

    def to_camel_case(self) -> None:
        def camel(words: list[str]) -> str:
            if not words:
                return ""
            first, *rest = words
            return first.lower() + "".join(word.capitalize() for word in rest)

        self._apply_transform(lambda s: camel(self._normalize_words(s)))

    def to_pascal_case(self) -> None:
        self._apply_transform(lambda s: "".join(word.capitalize() for word in self._normalize_words(s)))

    def to_kebab_case(self) -> None:
        self._apply_transform(lambda s: "-".join(self._normalize_words(s)).lower())

    def to_upper_snake_case(self) -> None:
        self._apply_transform(lambda s: "_".join(self._normalize_words(s)).upper())

    def insert_todo_comment(self) -> None:
        document = self._current_document()
        text = document.text
        text.insert(tk.INSERT, "# TODO: ")
        document.dirty = True
        self.update_title()

    def insert_iso_timestamp(self) -> None:
        document = self._current_document()
        document.text.insert(tk.INSERT, datetime.now().isoformat())
        document.dirty = True
        self.update_title()

    def add_line_numbers(self) -> None:
        def _add(text: str) -> str:
            return "\n".join(f"{idx + 1}: {line}" for idx, line in enumerate(text.splitlines()))

        self._apply_transform(_add)

    def remove_line_numbers(self) -> None:
        import re

        self._apply_transform(lambda s: "\n".join(re.sub(r"^\d+:\s*", "", line) for line in s.splitlines()))

    def align_assignments(self) -> None:
        def _align(text: str) -> str:
            lines = text.splitlines()
            positions = [line.find("=") for line in lines if "=" in line]
            if not positions:
                return text
            target = max(positions)
            aligned = []
            for line in lines:
                if "=" not in line:
                    aligned.append(line)
                    continue
                left, right = line.split("=", 1)
                aligned.append(f"{left.rstrip():<{target}} = {right.lstrip()}")
            return "\n".join(aligned)

        self._apply_transform(_align)

    def toggle_bullet_list(self) -> None:
        def _toggle(text: str) -> str:
            lines = text.splitlines()
            if all(line.strip().startswith("- ") for line in lines if line.strip()):
                return "\n".join(line.replace("- ", "", 1) if line.strip().startswith("- ") else line for line in lines)
            return "\n".join(f"- {line}" if line.strip() else line for line in lines)

        self._apply_transform(_toggle)

    def toggle_numbered_list(self) -> None:
        def _toggle(text: str) -> str:
            lines = text.splitlines()
            if all(line.lstrip().split(" ", 1)[0].rstrip(".").isdigit() for line in lines if line.strip()):
                return "\n".join(" ".join(line.split(" ", 1)[1:]) if line.strip() else line for line in lines)
            return "\n".join(f"{idx + 1}. {line}" if line.strip() else line for idx, line in enumerate(lines))

        self._apply_transform(_toggle)

    def transpose_characters(self) -> None:
        document = self._current_document()
        text = document.text
        index = text.index(tk.INSERT)
        line, column = map(int, index.split("."))
        if column < 1:
            return
        left = f"{line}.{column - 1}"
        right = f"{line}.{column}"
        chars = text.get(left, right)
        if len(chars) < 2:
            return
        text.delete(left, right)
        text.insert(left, chars[1] + chars[0])
        document.dirty = True
        self.update_title()

    def select_current_line(self) -> None:
        text = self._active_text()
        start, end = text.index("insert linestart"), text.index("insert lineend")
        text.tag_add(tk.SEL, start, end)
        text.mark_set(tk.INSERT, end)

    def select_word(self) -> None:
        text = self._active_text()
        start = text.index("insert wordstart")
        end = text.index("insert wordend")
        text.tag_add(tk.SEL, start, end)
        text.mark_set(tk.INSERT, end)

    def go_to_matching_bracket(self) -> None:
        pairs = {"(": ")", "[": "]", "{": "}"}
        text = self._active_text()
        current = text.get(tk.INSERT)
        for open_b, close_b in pairs.items():
            if current == open_b:
                match = text.search(close_b, tk.INSERT, stopindex="end")
                if match:
                    text.mark_set(tk.INSERT, match)
                return
            if current == close_b:
                match = text.search(open_b, tk.INSERT, backwards=True, stopindex="1.0")
                if match:
                    text.mark_set(tk.INSERT, match)
                return

    def collapse_spaces(self) -> None:
        import re

        self._apply_transform(lambda s: re.sub(r"\s+", " ", s))

    def pad_numbers(self) -> None:
        import re

        def _pad(text: str) -> str:
            return re.sub(r"\b(\d+)\b", lambda m: m.group(1).zfill(3), text)

        self._apply_transform(_pad)

    def strip_bom(self) -> None:
        self._apply_transform(lambda s: s.replace("\ufeff", ""))

    def normalize_double_quotes(self) -> None:
        self._apply_transform(lambda s: s.replace("'", '"'))

    def normalize_single_quotes(self) -> None:
        self._apply_transform(lambda s: s.replace('"', "'"))


def run() -> None:  # pragma: no cover - UI driven
    """Convenience wrapper to start the notepad application."""

    app = NotepadApp()
    app.run()
