# build-your-own-notepad

An educational project that demonstrates how to build a simple yet functional Notepad-like text editor using Python and Tkinter. It now mirrors the classic Notepad experience with File/Edit/Format/View menus, word wrap, zoom controls, and customizable fonts.

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install tk
```

> On some platforms Tkinter is bundled with Python and you may not need to install `tk` separately.

## Usage

Run the application from the project root:

```bash
python main.py
```

This launches a window with a full-featured text editor. Highlights include:

- **File**: New documents, open existing files, save/save-as, new window, and exit with unsaved-change prompts.
- **Edit**: Undo/redo, cut/copy/paste/delete, select all, and time/date insertion (F5).
- **Format**: Toggle word wrap and choose fonts and sizes from a curated list of code-friendly families with live previews.
- **View**: Zoom in/out/reset and show/hide the status bar.
- **Editor**: Scrollable text area with horizontal/vertical scrollbars and line/column status indicator.
- **Tabs**: Open multiple documents side by side in the same window, close them from the tab “✕”, double-click empty space to spawn new tabs, and use middle-click to close quickly.
- **Toolbar**: Icon-based quick actions that stay pinned under the menubar even after toggling visibility.
- **Command Palette**: Access more than 50 popular editing commands (case transforms, commenting, deduping, alignment, list toggles, wrapping helpers, line moves, etc.) via **Commands → Command Palette** or **Ctrl+Shift+P**.

Keyboard shortcuts like Ctrl+N/Ctrl+O/Ctrl+S, Ctrl+Z/Ctrl+Y, and Ctrl++/Ctrl+-/Ctrl+0 are supported.