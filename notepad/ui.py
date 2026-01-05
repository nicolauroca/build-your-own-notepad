"""User interface components for the notepad application."""

from __future__ import annotations

import tkinter as tk


class NotepadUI:
    """Encapsulates the Tkinter widgets for the notepad."""

    def __init__(
        self,
        root: tk.Tk,
        on_open,
        on_save,
        on_save_as,
        on_exit,
        on_content_change,
    ) -> None:
        self.root = root
        self.frame = tk.Frame(self.root)
        self.text = tk.Text(self.frame, wrap=tk.NONE, undo=True)

        self._build_menu(on_open, on_save, on_save_as, on_exit)
        self._build_editor(on_content_change)

    def _build_menu(self, on_open, on_save, on_save_as, on_exit) -> None:
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=on_open)
        file_menu.add_command(label="Save", command=on_save)
        file_menu.add_command(label="Save As...", command=on_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=on_exit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def _build_editor(self, on_content_change) -> None:
        self.frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.text.yview)

        self.text.bind("<KeyRelease>", on_content_change)
