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
        on_save_all,
        on_reload_file,
        on_open_recent,
        on_close_tab,
        on_close_all,
        on_close_other_tabs,
        on_close_tabs_left,
        on_close_tabs_right,
        on_reopen_closed_tab,
        on_duplicate_tab,
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
        on_toggle_toolbar,
        on_find,
        on_find_next,
        on_find_previous,
        on_replace,
        on_go_to,
        on_set_encoding,
        on_convert_encoding,
        on_content_change,
        on_cursor_move,
        on_tab_change,
        on_open_command_palette,
        on_change_theme,
    ) -> None:
        self.root = root
        self.themes = {
            "dark": {
                "background": "#0b1221",
                "panel": "#0f172a",
                "card": "#111827",
                "border": "#1f2937",
                "accent": "#7c3aed",
                "accent_alt": "#6366f1",
                "text": "#e5e7eb",
                "muted": "#9ca3af",
                "selection": "#312e81",
            },
            "light": {
                "background": "#f7f7fb",
                "panel": "#ececf5",
                "card": "#ffffff",
                "border": "#d7d7e0",
                "accent": "#2563eb",
                "accent_alt": "#1d4ed8",
                "text": "#1f2937",
                "muted": "#4b5563",
                "selection": "#c7d2fe",
            },
        }
        self.theme_var = tk.StringVar(value="dark")
        self.colors = self.themes[self.theme_var.get()]

        self._configure_style()

        self.frame = ttk.Frame(self.root, padding=(12, 10), style="Background.TFrame")
        self.notebook = ttk.Notebook(self.frame, style="Modern.TNotebook")
        self.text_widgets: dict[str, tk.Text] = {}
        self.status = tk.StringVar(value="Ln 1, Col 1")
        self.status_bar = ttk.Label(
            self.root, textvariable=self.status, anchor=tk.W, style="Status.TLabel"
        )
        self.word_wrap_var = tk.BooleanVar(value=False)
        self.status_bar_var = tk.BooleanVar(value=True)
        self.toolbar_var = tk.BooleanVar(value=True)
        self.encoding_var = tk.StringVar(value="UTF-8")
        self.on_change_theme = on_change_theme

        self.toolbar = ttk.Frame(self.root, style="Toolbar.TFrame")
        self._on_open_recent = on_open_recent
        self._on_close_tab = on_close_tab
        self._on_new_tab = on_new
        self._open_command_palette = on_open_command_palette
        self.commands_menu: tk.Menu | None = None

        # The editor frame must be packed before the toolbar so the toolbar can
        # reliably position itself directly beneath the menu using the
        # ``before`` parameter.
        self.frame.pack(fill=tk.BOTH, expand=True)

        self._build_menu(
            on_new,
            on_new_window,
            on_open,
            on_save,
            on_save_as,
            on_save_all,
            on_reload_file,
            on_open_recent,
            on_close_tab,
            on_close_all,
            on_close_other_tabs,
            on_close_tabs_left,
            on_close_tabs_right,
            on_reopen_closed_tab,
            on_duplicate_tab,
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
            on_toggle_toolbar,
            on_find,
            on_find_next,
            on_find_previous,
            on_replace,
            on_go_to,
            on_set_encoding,
            on_convert_encoding,
            on_open_command_palette,
            on_change_theme,
        )
        self._build_toolbar(
            on_new,
            on_open,
            on_save,
            on_save_as,
            on_save_all,
            on_reload_file,
            on_close_tab,
            on_undo,
            on_redo,
            on_cut,
            on_copy,
            on_paste,
            on_find,
            on_replace,
        )
        self._build_editor(on_content_change, on_cursor_move, on_tab_change)

    def _build_menu(
        self,
        on_new,
        on_new_window,
        on_open,
        on_save,
        on_save_as,
        on_save_all,
        on_reload_file,
        on_open_recent,
        on_close_tab,
        on_close_all,
        on_close_other_tabs,
        on_close_tabs_left,
        on_close_tabs_right,
        on_reopen_closed_tab,
        on_duplicate_tab,
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
        on_toggle_toolbar,
        on_find,
        on_find_next,
        on_find_previous,
        on_replace,
        on_go_to,
        on_set_encoding,
        on_convert_encoding,
        on_open_command_palette,
        on_change_theme,
    ) -> None:
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=on_new, accelerator="Ctrl+N")
        file_menu.add_command(label="New Window", command=on_new_window)
        file_menu.add_command(label="Open...", command=on_open, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=on_save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=on_save_as, accelerator="F12")
        file_menu.add_command(label="Save All", command=on_save_all, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Reload from Disk", command=on_reload_file)
        file_menu.add_separator()
        file_menu.add_command(label="Close", command=on_close_tab, accelerator="Ctrl+W")
        file_menu.add_command(label="Close All", command=on_close_all)
        file_menu.add_command(label="Close All Except This", command=on_close_other_tabs)
        file_menu.add_command(label="Close Tabs to the Left", command=on_close_tabs_left)
        file_menu.add_command(label="Close Tabs to the Right", command=on_close_tabs_right)
        file_menu.add_command(label="Reopen Closed Tab", command=on_reopen_closed_tab)
        file_menu.add_command(label="Duplicate Tab", command=on_duplicate_tab)
        file_menu.add_separator()
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Open Recent", menu=self.recent_menu)
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

        search_menu = tk.Menu(menubar, tearoff=0)
        search_menu.add_command(label="Find", command=on_find, accelerator="Ctrl+F")
        search_menu.add_command(label="Find Next", command=on_find_next, accelerator="F3")
        search_menu.add_command(label="Find Previous", command=on_find_previous, accelerator="Shift+F3")
        search_menu.add_command(label="Replace", command=on_replace, accelerator="Ctrl+H")
        search_menu.add_command(label="Go To", command=on_go_to, accelerator="Ctrl+G")

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
        view_menu.add_checkbutton(
            label="Toolbar", command=on_toggle_toolbar, variable=self.toolbar_var
        )
        view_menu.add_separator()
        view_menu.add_radiobutton(
            label="Dark Mode",
            value="dark",
            variable=self.theme_var,
            command=lambda: on_change_theme("dark"),
        )
        view_menu.add_radiobutton(
            label="Light Mode",
            value="light",
            variable=self.theme_var,
            command=lambda: on_change_theme("light"),
        )

        encoding_menu = tk.Menu(menubar, tearoff=0)
        encode_targets = ["ANSI", "UTF-8", "UTF-8-BOM", "UTF-16 LE", "UTF-16 BE"]
        for label in encode_targets:
            encoding_menu.add_radiobutton(
                label=f"Encode in {label}",
                value=label,
                variable=self.encoding_var,
                command=lambda l=label: on_set_encoding(l),
            )

        encoding_menu.add_separator()
        for label in encode_targets:
            encoding_menu.add_command(
                label=f"Convert to {label}", command=lambda l=label: on_convert_encoding(l)
            )

        self.commands_menu = tk.Menu(menubar, tearoff=0)
        self.commands_menu.add_command(label="Command Palette...", command=on_open_command_palette, accelerator="Ctrl+Shift+P")
        self.commands_menu.add_separator()

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        menubar.add_cascade(label="Search", menu=search_menu)
        menubar.add_cascade(label="Format", menu=format_menu)
        menubar.add_cascade(label="View", menu=view_menu)
        menubar.add_cascade(label="Encoding", menu=encoding_menu)
        menubar.add_cascade(label="Commands", menu=self.commands_menu)
        self.root.config(menu=menubar)

        self.root.bind_all("<Control-n>", lambda event: on_new())
        self.root.bind_all("<Control-o>", lambda event: on_open())
        self.root.bind_all("<Control-s>", lambda event: on_save())
        self.root.bind_all("<F12>", lambda event: on_save_as())
        self.root.bind_all("<Control-Shift-s>", lambda event: on_save_all())
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
        self.root.bind_all("<Control-f>", lambda event: on_find())
        self.root.bind_all("<Control-h>", lambda event: on_replace())
        self.root.bind_all("<Control-g>", lambda event: on_go_to())
        self.root.bind_all("<F3>", lambda event: on_find_next())
        self.root.bind_all("<Shift-F3>", lambda event: on_find_previous())
        self.root.bind_all("<Control-w>", lambda event: on_close_tab())
        self.root.bind_all("<Control-Shift-P>", lambda event: on_open_command_palette())

        self._build_tab_menu(
            on_close_tab,
            on_close_all,
            on_close_other_tabs,
            on_close_tabs_left,
            on_close_tabs_right,
            on_reopen_closed_tab,
            on_duplicate_tab,
        )

    def _text_theme_kwargs(self) -> dict[str, object]:
        return {
            "background": self.colors["card"],
            "foreground": self.colors["text"],
            "insertbackground": self.colors["accent_alt"],
            "selectbackground": self.colors["selection"],
            "selectforeground": self.colors["text"],
            "highlightthickness": 0,
            "bd": 0,
            "padx": 10,
            "pady": 8,
            "spacing2": 4,
        }

    def _configure_style(self) -> None:
        self.root.configure(bg=self.colors["background"])
        base_font = tkfont.nametofont("TkDefaultFont")
        base_font.configure(family="Segoe UI", size=10)
        icon_font_family = "Segoe UI Emoji" if "Segoe UI Emoji" in tkfont.families() else base_font.actual("family")
        self.icon_font = tkfont.Font(family=icon_font_family, size=12)
        strong_font = base_font.copy()
        strong_font.configure(weight="bold")
        small_font = base_font.copy()
        small_font.configure(size=9)
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("Background.TFrame", background=self.colors["background"])
        style.configure("Card.TFrame", background=self.colors["card"], borderwidth=0)
        style.configure("Toolbar.TFrame", background=self.colors["panel"], borderwidth=0)
        style.configure(
            "Toolbar.TButton",
            background=self.colors["panel"],
            foreground=self.colors["text"],
            padding=(10, 7),
            borderwidth=0,
            font=self.icon_font,
        )
        style.map(
            "Toolbar.TButton",
            background=[("active", self.colors["accent"]), ("pressed", self.colors["accent_alt"])],
            foreground=[("active", self.colors["text"])],
        )

        style.configure(
            "Modern.TNotebook",
            background=self.colors["background"],
            borderwidth=0,
            tabmargins=(10, 6, 10, 0),
        )
        style.configure(
            "Modern.TNotebook.Tab",
            background=self.colors["card"],
            foreground=self.colors["muted"],
            padding=(14, 9),
            font=strong_font,
            borderwidth=0,
        )
        style.map(
            "Modern.TNotebook.Tab",
            background=[("selected", self.colors["accent"]), ("active", self.colors["panel"])],
            foreground=[("selected", self.colors["text"]), ("active", self.colors["text"])],
        )

        style.configure(
            "Status.TLabel",
            background=self.colors["panel"],
            foreground=self.colors["muted"],
            padding=(12, 6),
            font=small_font,
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=self.colors["panel"],
            troughcolor=self.colors["card"],
            bordercolor=self.colors["panel"],
            arrowcolor=self.colors["text"],
        )
        style.configure(
            "Vertical.TScrollbar",
            background=self.colors["panel"],
            troughcolor=self.colors["card"],
            bordercolor=self.colors["panel"],
            arrowcolor=self.colors["text"],
        )

    def set_theme(self, mode: str) -> None:
        if mode not in self.themes:
            return

        self.theme_var.set(mode)
        self.colors = self.themes[mode]
        self._configure_style()
        self.frame.configure(style="Background.TFrame")
        self.toolbar.configure(style="Toolbar.TFrame")
        self.status_bar.configure(style="Status.TLabel")
        self.notebook.configure(style="Modern.TNotebook")
        for child in self.toolbar.winfo_children():
            child.configure(style="Toolbar.TButton")
        for text in self.text_widgets.values():
            text.configure(**self._text_theme_kwargs())

    def set_selected_encoding(self, label: str) -> None:
        """Highlight the active encoding in the Encoding menu."""

        if label:
            self.encoding_var.set(label)

    def _build_toolbar(
        self,
        on_new,
        on_open,
        on_save,
        on_save_as,
        on_save_all,
        on_reload_file,
        on_close_tab,
        on_undo,
        on_redo,
        on_cut,
        on_copy,
        on_paste,
        on_find,
        on_replace,
    ) -> None:
        buttons = [
            ("📄", "New file", on_new),
            ("📂", "Open", on_open),
            ("💾", "Save", on_save),
            ("📝", "Save As", on_save_as),
            ("🧰", "Save All", on_save_all),
            ("🔄", "Reload", on_reload_file),
            ("❌", "Close tab", on_close_tab),
            ("↩", "Undo", on_undo),
            ("↪", "Redo", on_redo),
            ("✂", "Cut", on_cut),
            ("📋", "Copy", on_copy),
            ("📥", "Paste", on_paste),
            ("🔍", "Find", on_find),
            ("♻", "Replace", on_replace),
        ]

        for symbol, tooltip, command in buttons:
            btn = ttk.Button(
                self.toolbar,
                text=symbol,
                command=command,
                style="Toolbar.TButton",
                width=3,
            )
            btn.pack(side=tk.LEFT, padx=3, pady=6)
            btn.bind("<Enter>", lambda e, t=tooltip: self.status.set(t))
            btn.bind("<Leave>", lambda e: self.status.set(self.status.get()))

        self.toolbar.pack(side=tk.TOP, fill=tk.X, before=self.frame, pady=(4, 2))

    def _build_editor(self, on_content_change, on_cursor_move, on_tab_change) -> None:
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", on_tab_change)
        self.notebook.bind("<Button-3>", self._open_tab_menu)
        self.notebook.bind("<Button-1>", self._maybe_close_tab, add="+")
        self.notebook.bind("<Button-2>", self._close_tab_with_middle_click, add="+")
        self.notebook.bind("<Double-Button-1>", self._open_new_tab, add="+")

        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def add_tab(self, title: str, text_font: tkfont.Font, on_content_change, on_cursor_move):
        frame = ttk.Frame(self.notebook, style="Card.TFrame")
        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        text = tk.Text(
            frame,
            wrap=tk.NONE,
            undo=True,
            font=text_font,
            **self._text_theme_kwargs(),
        )
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 0), pady=(2, 0))
        text.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        y_scrollbar.configure(command=text.yview)
        x_scrollbar.configure(command=text.xview)

        text.bind("<KeyRelease>", on_content_change)
        text.bind("<ButtonRelease>", on_cursor_move)
        text.bind("<Motion>", on_cursor_move)

        self.notebook.add(frame, text=self._with_close_icon(title))
        tab_id = str(frame)
        self.notebook.select(frame)
        self.text_widgets[tab_id] = text
        return tab_id, text

    def get_current_tab(self) -> tuple[str, tk.Text | None]:
        tab_id = self.notebook.select()
        return tab_id, self.text_widgets.get(tab_id)

    def set_tab_title(self, tab_id: str, title: str) -> None:
        if tab_id:
            self.notebook.tab(tab_id, text=self._with_close_icon(title))

    def select_tab(self, tab_id: str) -> None:
        if tab_id:
            self.notebook.select(tab_id)

    def remove_tab(self, tab_id: str) -> None:
        if tab_id:
            self.notebook.forget(tab_id)
            self.text_widgets.pop(tab_id, None)

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

    def toggle_toolbar(self, visible: bool) -> None:
        if visible:
            self.toolbar.pack(side=tk.TOP, fill=tk.X, before=self.frame)
        else:
            self.toolbar.pack_forget()
        self.toolbar_var.set(visible)

    def _build_tab_menu(
        self,
        on_close_tab,
        on_close_all,
        on_close_other_tabs,
        on_close_tabs_left,
        on_close_tabs_right,
        on_reopen_closed_tab,
        on_duplicate_tab,
    ) -> None:
        self.tab_menu = tk.Menu(self.root, tearoff=0)
        self.tab_menu.add_command(label="Close", command=on_close_tab)
        self.tab_menu.add_command(label="Close All", command=on_close_all)
        self.tab_menu.add_command(label="Close All But This", command=on_close_other_tabs)
        self.tab_menu.add_command(label="Close Tabs to the Left", command=on_close_tabs_left)
        self.tab_menu.add_command(label="Close Tabs to the Right", command=on_close_tabs_right)
        self.tab_menu.add_separator()
        self.tab_menu.add_command(label="Reopen Closed Tab", command=on_reopen_closed_tab)
        self.tab_menu.add_command(label="Duplicate", command=on_duplicate_tab)

    def _open_tab_menu(self, event) -> None:  # pragma: no cover - UI driven
        try:
            index = self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return
        tab_id = self.notebook.tabs()[index]
        self.notebook.select(tab_id)
        self.tab_menu.tk_popup(event.x_root, event.y_root)

    def _maybe_close_tab(self, event) -> None:  # pragma: no cover - UI driven
        try:
            index = self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return

        x, y, width, height = self.notebook.bbox(index)
        if not (x <= event.x <= x + width and y <= event.y <= y + height):
            return

        close_region_start = x + width - 24
        if close_region_start <= event.x <= x + width:
            tab_id = self.notebook.tabs()[index]
            self.notebook.select(tab_id)
            self._on_close_tab()

    def _close_tab_with_middle_click(self, event) -> None:  # pragma: no cover - UI driven
        try:
            index = self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return
        tab_id = self.notebook.tabs()[index]
        self.notebook.select(tab_id)
        self._on_close_tab()

    def _open_new_tab(self, event) -> None:  # pragma: no cover - UI driven
        try:
            self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            # Double click on empty space opens a new tab
            self._on_new_tab()

    def tab_order(self) -> list[str]:
        return list(self.notebook.tabs())

    def update_recent_files(self, recent: list[str]) -> None:
        self.recent_menu.delete(0, tk.END)
        if not recent:
            self.recent_menu.add_command(label="(empty)", state=tk.DISABLED)
        else:
            for path in recent:
                self.recent_menu.add_command(label=path, command=lambda p=path: self._on_open_recent(p))

    def update_commands_menu(self, commands: list[dict[str, object]]) -> None:
        if not self.commands_menu:
            return

        self.commands_menu.delete(2, tk.END)
        if not commands:
            self.commands_menu.add_command(label="(no commands)", state=tk.DISABLED)
            return

        for command in commands[:15]:
            label = f"{command['icon']} {command['name']}"
            self.commands_menu.add_command(label=label, command=command["action"])

    def prompt_for_font_choice(self, initial_family: str, initial_size: int) -> tuple[str, int] | None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose Font")
        dialog.geometry("420x420")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Select a font optimized for code:").pack(anchor=tk.W, padx=10, pady=(10, 2))

        sample_var = tk.StringVar(value="The quick brown fox jumps over the lazy dog. 0123456789")
        preview = tk.Label(dialog, textvariable=sample_var, relief=tk.SUNKEN, padx=6, pady=6)
        preview.pack(fill=tk.X, padx=10, pady=6)

        container = tk.Frame(dialog)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        scrollbar = tk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = tk.Listbox(container, yscrollcommand=scrollbar.set)
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        size_var = tk.IntVar(value=initial_size)
        size_spin = tk.Spinbox(dialog, from_=8, to=48, textvariable=size_var, width=5)
        size_spin.pack(anchor=tk.W, padx=10, pady=(4, 10))

        code_friendly = self._code_friendly_fonts()
        for family in code_friendly:
            listbox.insert(tk.END, family)

        def on_select(event=None):
            selection = listbox.curselection()
            if not selection:
                return
            family = listbox.get(selection[0])
            preview.configure(font=(family, size_var.get()))

        def accept():
            selection = listbox.curselection()
            if not selection:
                dialog.destroy()
                return
            dialog.result = (listbox.get(selection[0]), int(size_var.get()))
            dialog.destroy()

        def cancel():
            dialog.result = None
            dialog.destroy()

        listbox.bind("<<ListboxSelect>>", on_select)
        preview.configure(font=(initial_family, initial_size))

        btn_row = tk.Frame(dialog)
        btn_row.pack(fill=tk.X, padx=10, pady=(4, 8))
        tk.Button(btn_row, text="OK", command=accept).pack(side=tk.RIGHT, padx=4)
        tk.Button(btn_row, text="Cancel", command=cancel).pack(side=tk.RIGHT, padx=4)

        if initial_family in code_friendly:
            idx = code_friendly.index(initial_family)
            listbox.selection_set(idx)
            listbox.see(idx)
            preview.configure(font=(initial_family, initial_size))

        dialog.wait_window()
        return getattr(dialog, "result", None)

    def _code_friendly_fonts(self) -> list[str]:
        candidates = []
        keywords = ("Mono", "Code", "Console", "Fixed", "Courier", "Hack", "Menlo", "Cascadia", "Jet")
        for family in tkfont.families():
            if any(key.lower() in family.lower() for key in keywords):
                candidates.append(family)
        return sorted(dict.fromkeys(candidates)) or ["Courier New", "Consolas", "Menlo", "Monaco"]

    def _with_close_icon(self, title: str) -> str:
        return f"{title}   ✕"
