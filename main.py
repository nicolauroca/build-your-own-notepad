"""Entry point for launching the Tkinter notepad application."""

from notepad.app import NotepadApp


if __name__ == "__main__":
    app = NotepadApp()
    app.run()
