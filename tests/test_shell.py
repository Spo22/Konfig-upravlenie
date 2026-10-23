"""Tests for startup settings and early shell commands."""

import tempfile
import unittest
from pathlib import Path

from src.script import run_script
from src.settings import Settings, parse_cli
from src.shell import Shell


class ReplTests(unittest.TestCase):
    """Verify parsing, configuration and script handling."""

    def setUp(self):
        """Create a fresh configured shell."""
        self.temp = tempfile.TemporaryDirectory()
        self.shell = Shell(Settings(Path(self.temp.name)))

    def tearDown(self):
        """Remove the temporary VFS source."""
        self.temp.cleanup()

    def test_ls(self):
        """List files in the in-memory VFS."""
        (Path(self.temp.name) / "readme.txt").write_text("before")
        self.assertEqual(self.shell.execute("ls").text, "")
        self.assertFalse(self.shell.execute("ls missing.txt").ok)

    def test_unknown_command(self):
        """Reject names not supported by the emulator."""
        self.assertFalse(self.shell.execute("badcommand").ok)

    def test_bad_arguments(self):
        """Report unsupported arguments."""
        self.assertFalse(self.shell.execute("cd x y").ok)

    def test_cd_root(self):
        """Keep current directory within the virtual root."""
        result = self.shell.execute("cd /")
        self.assertTrue(result.ok)
        self.assertEqual(self.shell.cwd, "/")

    def test_whoami(self):
        """Display the current real user's login name."""
        self.assertTrue(self.shell.execute("whoami").text)
        self.assertFalse(self.shell.execute("whoami extra").ok)

    def test_calendar(self):
        """Print supported calendars and reject invalid months."""
        self.assertIn("2024", self.shell.execute("cal 2 2024").text)
        self.assertIn("2026", self.shell.execute("cal 2026").text)
        self.assertFalse(self.shell.execute("cal 13 2026").ok)

    def test_exit(self):
        """Exit is a recognized terminal command."""
        self.assertTrue(self.shell.execute("exit").exit_requested)

    def test_cli_config(self):
        """Parse explicit VFS and startup script paths."""
        settings = parse_cli(["--vfs", ".", "--script", "foo.txt"])
        self.assertTrue(settings.vfs_path.is_absolute())
        self.assertEqual(settings.script_path.name, "foo.txt")

    def test_conf_dump(self):
        """Show settings as key-value pairs."""
        result = self.shell.execute("conf-dump")
        self.assertIn("vfs_path=", result.text)
        self.assertIn("script_path=", result.text)

    def test_stop_script_at_error(self):
        """Stop running the startup script after the first failure."""
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "script.txt"
            script.write_text("ls\ninvalid\ncd\n", encoding="utf-8")
            lines = []
            self.assertFalse(run_script(self.shell, script, lines.append))
            self.assertFalse(any(" $ cd" in line for line in lines))
            self.assertTrue(any("строке 2" in line for line in lines))


if __name__ == "__main__":
    unittest.main()
