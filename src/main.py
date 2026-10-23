"""Application entry point."""

from src.gui import EmulatorGUI
from src.script import run_script
from src.settings import parse_cli
from src.shell import Shell


def run_headless(shell):
    """Run a startup script or interactive REPL in a regular terminal."""
    print("Настройки запуска:")
    print(shell.execute("conf-dump").text)
    script_path = shell.settings.script_path
    if script_path is not None:
        return 0 if run_script(shell, script_path, print) else 1
    while True:
        try:
            line = input(f"{shell.cwd} $ ")
        except EOFError:
            return 0
        result = shell.execute(line)
        if result.text:
            print(result.text)
        if result.exit_requested:
            return 0


def main(argv=None):
    """Choose GUI by default and terminal mode for automated checking."""
    settings = parse_cli(argv)
    shell = Shell(settings)
    if settings.headless:
        try:
            return run_headless(shell)
        except (OSError, UnicodeError) as error:
            print(f"Ошибка загрузки стартового скрипта: {error}")
            return 1
    gui = EmulatorGUI(shell)
    gui.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
