"""User interface components for the notepad application."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk


class NotepadUI:
    """Encapsulates the Tkinter widgets for the notepad."""

    def __init__(
        self,
        root: tk.Tk,
        text_font: tkfont.Font,
        on_new,
        on_new_window,
        on_open,
        on_save,
        on_save_as,
        on_exit,
        on_undo,
        on_redo,
        on_cut,
        on_copy,
        on_paste,
        on_delete,
        on_select_all,
        on_time_date,
        on_word_wrap,
        on_choose_font,
        on_zoom_in,
        on_zoom_out,
        on_zoom_reset,
        on_toggle_status_bar,
        on_content_change,
        on_cursor_move,
        on_tab_change,
    ) -> None:
        self.root = root
        self.frame = tk.Frame(self.root)
        self.notebook = ttk.Notebook(self.frame)
        self.text_widgets: dict[str, tk.Text] = {}
        self.status = tk.StringVar(value="Ln 1, Col 1")
        self.status_bar = tk.Label(self.root, textvariable=self.status, anchor=tk.W)
        self.word_wrap_var = tk.BooleanVar(value=False)
        self.status_bar_var = tk.BooleanVar(value=True)

        self._build_menu(
            on_new,
            on_new_window,
            on_open,
            on_save,
            on_save_as,
            on_exit,
            on_undo,
            on_redo,
            on_cut,
            on_copy,
            on_paste,
            on_delete,
            on_select_all,
            on_time_date,
            on_word_wrap,
            on_choose_font,
            on_zoom_in,
            on_zoom_out,
            on_zoom_reset,
            on_toggle_status_bar,
        )
        self._build_editor(on_content_change, on_cursor_move, on_tab_change)

    def _build_menu(
        self,
        on_new,
        on_new_window,
        on_open,
        on_save,
        on_save_as,
        on_exit,
        on_undo,
        on_redo,
        on_cut,
        on_copy,
        on_paste,
        on_delete,
        on_select_all,
        on_time_date,
        on_word_wrap,
        on_choose_font,
        on_zoom_in,
        on_zoom_out,
        on_zoom_reset,
        on_toggle_status_bar,
    ) -> None:
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=on_new, accelerator="Ctrl+N")
        file_menu.add_command(label="New Window", command=on_new_window)
        file_menu.add_command(label="Open...", command=on_open, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=on_save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=on_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=on_exit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=on_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=on_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=on_cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=on_copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=on_paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Delete", command=on_delete)
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=on_select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Time/Date", command=on_time_date, accelerator="F5")

        format_menu = tk.Menu(menubar, tearoff=0)
        format_menu.add_checkbutton(
            label="Word Wrap", command=on_word_wrap, variable=self.word_wrap_var
        )
        format_menu.add_command(label="Font...", command=on_choose_font)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=on_zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=on_zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Restore Default Zoom", command=on_zoom_reset)
        view_menu.add_separator()
        view_menu.add_checkbutton(
            label="Status Bar", command=on_toggle_status_bar, variable=self.status_bar_var
        )

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        menubar.add_cascade(label="Format", menu=format_menu)
        menubar.add_cascade(label="View", menu=view_menu)
        self.root.config(menu=menubar)

        self.root.bind_all("<Control-n>", lambda event: on_new())
        self.root.bind_all("<Control-o>", lambda event: on_open())
        self.root.bind_all("<Control-s>", lambda event: on_save())
        self.root.bind_all("<Control-Shift-S>", lambda event: on_save_as())
        self.root.bind_all("<Control-z>", lambda event: on_undo())
        self.root.bind_all("<Control-y>", lambda event: on_redo())
        self.root.bind_all("<Control-x>", lambda event: on_cut())
        self.root.bind_all("<Control-c>", lambda event: on_copy())
        self.root.bind_all("<Control-v>", lambda event: on_paste())
        self.root.bind_all("<Control-a>", lambda event: on_select_all())
        self.root.bind_all("<F5>", lambda event: on_time_date())
        self.root.bind_all("<Control-plus>", lambda event: on_zoom_in())
        self.root.bind_all("<Control-minus>", lambda event: on_zoom_out())
        self.root.bind_all("<Control-0>", lambda event: on_zoom_reset())

    def _build_editor(self, on_content_change, on_cursor_move, on_tab_change) -> None:
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", on_tab_change)

        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def add_tab(self, title: str, text_font: tkfont.Font, on_content_change, on_cursor_move):
        frame = tk.Frame(self.notebook)
        y_scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        text = tk.Text(frame, wrap=tk.NONE, undo=True, font=text_font)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        y_scrollbar.configure(command=text.yview)
        x_scrollbar.configure(command=text.xview)

        text.bind("<KeyRelease>", on_content_change)
        text.bind("<ButtonRelease>", on_cursor_move)
        text.bind("<Motion>", on_cursor_move)

        self.notebook.add(frame, text=title)
        tab_id = str(frame)
        self.notebook.select(frame)
        self.text_widgets[tab_id] = text
        return tab_id, text

    def get_current_tab(self) -> tuple[str, tk.Text | None]:
        tab_id = self.notebook.select()
        return tab_id, self.text_widgets.get(tab_id)

    def set_tab_title(self, tab_id: str, title: str) -> None:
        if tab_id:
            self.notebook.tab(tab_id, text=title)

    def select_tab(self, tab_id: str) -> None:
        if tab_id:
            self.notebook.select(tab_id)

    def set_word_wrap(self, enabled: bool) -> None:
        for text in self.text_widgets.values():
            text.configure(wrap=tk.WORD if enabled else tk.NONE)
        self.word_wrap_var.set(enabled)

    def set_status(self, text: str) -> None:
        self.status.set(text)

    def toggle_status_bar(self) -> None:
        if self.status_bar.winfo_viewable():
            self.status_bar.pack_forget()
            self.status_bar_var.set(False)
        else:
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            self.status_bar_var.set(True)
