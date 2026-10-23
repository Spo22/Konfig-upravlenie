"""Application entry point."""

from src.gui import EmulatorGUI
from src.shell import Shell


def main():
    """Start the graphical shell emulator."""
    gui = EmulatorGUI(Shell())
    gui.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
