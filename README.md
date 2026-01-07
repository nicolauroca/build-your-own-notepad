# build-your-own-notepad

An educational project that demonstrates how to build a simple yet functional Notepad-like text editor using Python and Tkinter. It mirrors the classic Notepad experience with File/Edit/Format/View menus, word wrap, zoom controls, and customizable fonts.

This MVP was created end-to-end with the help of **OpenAI Codex** to explore how a code-focused AI can guide a complete, stable, ready-to-use editor. The result is a lightweight alternative to Notepad with several extra utilities and roughly half the memory footprint of the traditional application.

## How to reproduce this workflow with OpenAI Codex

1. **Define clear requirements**: document scope (menus, shortcuts, tabs, formatting, etc.) and set the goal of a closed-but-functional MVP.
2. **Iterate with Codex**: request code generation by modules (UI, file operations, editing commands) and validate each block locally.
3. **Add documentation and comments**: ask Codex for docstrings and notes that explain design decisions so contributors can follow the flow.
4. **Test and refine**: manually verify key behaviors (open/save, tabs, advanced commands) and request incremental adjustments.
5. **Finalize the MVP**: freeze scope after requirements are met, publish the code, and set clear maintenance expectations.

> Note: the project ships as a closed MVP with open source code for future enhancements and community contributions. Given the abundance of Notepad alternatives, no active maintenance is planned.

## Requirements

- Python 3.10+ (Tkinter requires a desktop environment).
- Tkinter (bundled with many Python distributions).

If Tkinter is missing on Linux, install it with your package manager (for example, `sudo apt-get install python3-tk` on Debian/Ubuntu).

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> On some platforms Tkinter is bundled with Python and you may not need to install additional system packages.

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

## Project structure

- `main.py`: Application entry point that launches the Tkinter UI.
- `notepad/`: Core editor implementation (menus, commands, tab management, and UI behavior).
- `requirements.txt`: Runtime Python dependencies (kept minimal because Tkinter is standard).

## Contributing

This project is intentionally scoped as a minimal, self-contained MVP. If you want to extend it (new commands, more themes, or persistence enhancements), please open an issue to discuss scope before submitting a pull request.
