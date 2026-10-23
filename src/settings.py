"""Command-line settings for the emulator."""

import argparse
from dataclasses import dataclass
from pathlib import Path


DEFAULT_VFS = Path(__file__).resolve().parents[1] / "examples/vfs/minimal"


@dataclass(frozen=True)
class Settings:
    """Resolved paths and optional headless test mode."""

    vfs_path: Path
    script_path: Path | None = None
    headless: bool = False


def parse_cli(argv=None):
    """Parse the VFS and startup script command-line parameters."""
    parser = argparse.ArgumentParser(
        description="Эмулятор UNIX-подобной оболочки (вариант 25)",
    )
    parser.add_argument("--vfs", type=Path, default=DEFAULT_VFS)
    parser.add_argument("--script", type=Path)
    parser.add_argument(
        "--headless", action="store_true",
        help="режим терминала для автоматизированных проверок",
    )
    args = parser.parse_args(argv)
    vfs_path = args.vfs.expanduser().resolve()
    script_path = args.script.expanduser().resolve() if args.script else None
    return Settings(vfs_path, script_path, args.headless)
