"""Command parsing and execution for the shell emulator."""

from dataclasses import dataclass

from src.vfs import VirtualFileSystem


@dataclass(frozen=True)
class Result:
    """One command's text, outcome and exit request."""

    text: str = ""
    ok: bool = True
    exit_requested: bool = False


class Shell:
    """Run simple space-delimited shell commands."""

    def __init__(self, settings):
        """Store parsed launch settings."""
        self.settings = settings
        self.vfs = VirtualFileSystem(settings.vfs_path)

    @property
    def cwd(self):
        """Return the displayed current directory."""
        return self.vfs.cwd

    def execute(self, line):
        """Parse and execute a line, reporting command errors."""
        parts = line.strip().split()
        if not parts:
            return Result()
        name, *args = parts
        commands = {
            "ls": self._stub,
            "cd": self._stub,
            "exit": self._exit,
            "conf-dump": self._conf_dump,
        }
        handler = commands.get(name)
        if handler is None:
            return Result(f"Ошибка: неизвестная команда: {name}", False)
        return handler(name, args)

    def _stub(self, name, args):
        """Print command name and arguments in the REPL stage."""
        if len(args) > 1:
            return Result(f"Ошибка: {name}: слишком много аргументов", False)
        return Result(f"{name}: args={args}")

    def _conf_dump(self, _name, args):
        """Display key-value launch settings."""
        if args:
            return Result("Ошибка: conf-dump: аргументы запрещены", False)
        script = self.settings.script_path
        lines = (
            f"vfs_path={self.settings.vfs_path}",
            f"script_path={script if script is not None else '(нет)'}",
        )
        return Result("\n".join(lines))

    def _exit(self, _name, args):
        """End a REPL session when no arguments are passed."""
        if args:
            return Result("Ошибка: exit: аргументы не поддерживаются", False)
        return Result("Завершение работы.", exit_requested=True)
