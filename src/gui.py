"""Tkinter graphical interface for the shell emulator."""

import getpass
import socket
import tkinter as tk
from tkinter.scrolledtext import ScrolledText


class EmulatorGUI:
    """Display a command-line conversation inside a GUI window."""

    def __init__(self, shell):
        """Construct a terminal-style window for a shell."""
        self.shell = shell
        self.root = tk.Tk()
        user_host = f"{getpass.getuser()}@{socket.gethostname()}"
        self.root.title(f"Эмулятор - [{user_host}]")
        self.root.geometry("820x530")
        self.output = ScrolledText(
            self.root, wrap="word", state="disabled",
            bg="#171b26", fg="#e5e9f0", insertbackground="white",
            font=("Consolas", 12), padx=12, pady=12,
        )
        self.output.pack(fill="both", expand=True)
        self.entry = tk.Entry(self.root, font=("Consolas", 12))
        self.entry.pack(fill="x", padx=8, pady=8)
        self.entry.bind("<Return>", self._submit)
        self.entry.focus_set()
        self.write("Эмулятор UNIX-подобной оболочки, вариант 25")

    def write(self, message):
        """Append a line of text to the read-only output area."""
        self.output.configure(state="normal")
        self.output.insert("end", message + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def process(self, line):
        """Echo and execute an entered command in the shell."""
        self.write(f"{self.shell.cwd} $ {line}")
        result = self.shell.execute(line)
        if result.text:
            self.write(result.text)
        if result.exit_requested:
            self.root.after(200, self.root.destroy)
        return result

    def _submit(self, _event):
        """Handle pressing Enter in the input field."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.process(line)

    def run(self):
        """Launch the Tkinter event loop."""
        self.root.mainloop()
