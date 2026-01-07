# build-your-own-notepad

An educational project that demonstrates how to build a simple yet functional Notepad-like text editor using Python and Tkinter. It now mirrors the classic Notepad experience with File/Edit/Format/View menus, word wrap, zoom controls, and customizable fonts.

This MVP was creado íntegramente con la ayuda de **OpenAI Codex**, explorando cómo una IA especializada en código puede conducir a un editor completo, estable y listo para usarse. El resultado es una alternativa ligera a Notepad con varias utilidades extra y un consumo de memoria aproximado de la mitad frente a la aplicación tradicional.

## Cómo reproducir este flujo con OpenAI Codex

1. **Definir requisitos claros**: documenta el alcance (menús, atajos, pestañas, formato, etc.) y fija que el objetivo es un MVP cerrado pero funcional.
2. **Iterar con Codex**: solicita generación de código por módulos (UI, operaciones de archivo, comandos de edición) y valida cada bloque en ejecución local.
3. **Añadir documentación y comentarios**: pide a Codex docstrings y anotaciones que expliquen decisiones de diseño, para que cualquier contribuidor entienda el flujo.
4. **Probar y refinar**: verifica manualmente los comportamientos clave (abrir/guardar, pestañas, comandos avanzados) y solicita a Codex ajustes incrementales.
5. **Cerrar el MVP**: congela el alcance tras cumplir los requisitos, publica el código y deja claras las expectativas de mantenimiento.

> Nota: el proyecto se publica como un MVP cerrado, con código abierto para evolutivos y contribuciones de la comunidad. Dada la abundancia de alternativas a Notepad ya disponibles, no se prevé un mantenimiento activo.

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