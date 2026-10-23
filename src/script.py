"""Startup script interpreter, stopping at the first command error."""

from pathlib import Path


def run_script(shell, script_path, write, on_exit=None):
    """Echo commands and output, stopping at the first error."""
    contents = Path(script_path).read_text(encoding="utf-8-sig")
    for number, raw_line in enumerate(contents.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        write(f"{shell.cwd} $ {line}")
        result = shell.execute(line)
        if result.text:
            write(result.text)
        if not result.ok:
            write(f"Скрипт остановлен из-за ошибки на строке {number}.")
            return False
        if result.exit_requested:
            if on_exit is not None:
                on_exit()
            return True
    return True
