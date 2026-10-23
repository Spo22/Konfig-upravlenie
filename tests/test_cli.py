"""Subprocess tests for startup scripts and headless operation."""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/vfs/deep"
SCRIPTS = ROOT / "examples/startup"


class HeadlessTests(unittest.TestCase):
    """Verify startup script status codes and output."""

    def _run(self, script):
        """Launch the emulator without requiring a display."""
        args = (
            sys.executable, "-m", "src.main", "--headless",
            "--vfs", str(FIXTURE), "--script", str(SCRIPTS / script),
        )
        return subprocess.run(
            args, cwd=ROOT, text=True, capture_output=True,
            check=False,
        )

    def test_all_commands(self):
        """Execute complete scenario with successful exit status."""
        result = self._run("all_commands.txt")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("$ mkdir reports", result.stdout)
        self.assertIn("results", result.stdout)
        self.assertFalse((FIXTURE / "projects/python/reports").exists())

    def test_script_error_stops(self):
        """Stop on a duplicate virtual directory creation."""
        result = self._run("mkdir_errors.txt")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Скрипт остановлен", result.stdout)

    def test_exit_stops_script(self):
        """Do not run commands that follow an exit command."""
        result = self._run("exit_example.txt")
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("$ ls", result.stdout)

    def test_missing_vfs(self):
        """Reject loading an inaccessible VFS directory."""
        args = (
            sys.executable, "-m", "src.main", "--headless",
            "--vfs", str(FIXTURE / "missing"),
        )
        result = subprocess.run(
            args, cwd=ROOT, text=True, capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Ошибка VFS", result.stderr)


if __name__ == "__main__":
    unittest.main()
