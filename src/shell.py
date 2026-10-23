"""Command parsing and execution for the shell emulator."""

import calendar
import getpass
from dataclasses import dataclass
from datetime import date

from src.vfs import VirtualFileSystem, VirtualFileSystemError


MIN_YEAR = 1
MAX_YEAR = 9999
MIN_MONTH = 1
MAX_MONTH = 12


@dataclass(frozen=True)
class Result:
    """One command's text, outcome and exit request."""

    text: str = ""
    ok: bool = True
    exit_requested: bool = False


class Shell:
    """Interpret commands using only the virtual filesystem."""

    def __init__(self, settings):
        """Store settings and read the VFS into process memory."""
        self.settings = settings
        self.vfs = VirtualFileSystem(settings.vfs_path)

    @property
    def cwd(self):
        """Return the UNIX-style current virtual directory."""
        return self.vfs.cwd

    def execute(self, line):
        """Parse a space-delimited line and execute one command."""
        parts = line.strip().split()
        if not parts:
            return Result()
        name, *args = parts
        commands = {
            "ls": self._ls,
            "cd": self._cd,
            "exit": self._exit,
            "conf-dump": self._conf_dump,
            "cal": self._cal,
            "whoami": self._whoami,
            "mkdir": self._mkdir,
        }
        handler = commands.get(name)
        if handler is None:
            return Result(f"Ошибка: неизвестная команда: {name}", False)
        try:
            return handler(args)
        except VirtualFileSystemError as error:
            return Result(f"Ошибка: {name}: {error}", False)

    def _ls(self, args):
        """List a virtual directory or display a filename."""
        if len(args) > 1:
            return Result("Ошибка: ls: слишком много аргументов", False)
        path = args[0] if args else "."
        names = self.vfs.list_directory(path)
        return Result("\n".join(names))

    def _cd(self, args):
        """Move to the chosen virtual directory, or to root."""
        if len(args) > 1:
            return Result("Ошибка: cd: слишком много аргументов", False)
        self.vfs.change_directory(args[0] if args else "/")
        return Result()

    def _mkdir(self, args):
        """Create a single directory only in the in-memory VFS."""
        if len(args) != 1:
            return Result("Ошибка: mkdir: требуется один путь", False)
        self.vfs.mkdir(args[0])
        return Result()

    def _cal(self, args):
        """Display the current month, a year, or a selected month."""
        try:
            month, year = self._calendar_args(args)
            if month is None:
                return Result(calendar.calendar(year))
            return Result(calendar.month(year, month))
        except (ValueError, OverflowError):
            return Result("Ошибка: cal: ожидается cal [год] "
                          "или cal [месяц] [год]", False)

    @staticmethod
    def _calendar_args(args):
        """Validate arguments and convert them into a year/month pair."""
        today = date.today()
        if not args:
            return today.month, today.year
        if len(args) == 1:
            year = int(args[0])
            if not MIN_YEAR <= year <= MAX_YEAR:
                raise ValueError("Недопустимый год")
            return None, year
        if len(args) == 2:
            month, year = int(args[0]), int(args[1])
            if not MIN_MONTH <= month <= MAX_MONTH:
                raise ValueError("Недопустимый месяц")
            if not MIN_YEAR <= year <= MAX_YEAR:
                raise ValueError("Недопустимый год")
            return month, year
        raise ValueError("Слишком много аргументов")

    @staticmethod
    def _whoami(args):
        """Display the real OS username, not a virtual identity."""
        if args:
            return Result("Ошибка: whoami: аргументы запрещены", False)
        return Result(getpass.getuser())

    def _conf_dump(self, args):
        """Display launch settings as key-value pairs."""
        if args:
            return Result("Ошибка: conf-dump: аргументы запрещены", False)
        script = self.settings.script_path
        lines = (
            f"vfs_path={self.settings.vfs_path}",
            f"script_path={script if script is not None else '(нет)'}",
        )
        return Result("\n".join(lines))

    @staticmethod
    def _exit(args):
        """Request termination of an interactive session."""
        if args:
            return Result("Ошибка: exit: аргументы не поддерживаются", False)
        return Result("Завершение работы.", exit_requested=True)
