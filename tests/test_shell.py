"""Early-stage tests for basic shell commands."""

import unittest

from src.shell import Shell


class ReplTests(unittest.TestCase):
    """Verify command parsing and error handling."""

    def setUp(self):
        """Create a fresh shell."""
        self.shell = Shell()

    def test_stub_command(self):
        """Show parsed arguments for early commands."""
        self.assertEqual(self.shell.execute("ls x").text, "ls: args=['x']")

    def test_unknown_command(self):
        """Reject names not supported by the emulator."""
        self.assertFalse(self.shell.execute("badcommand").ok)

    def test_bad_arguments(self):
        """Report unsupported arguments."""
        self.assertFalse(self.shell.execute("cd x y").ok)

    def test_exit(self):
        """Exit is a recognized terminal command."""
        self.assertTrue(self.shell.execute("exit").exit_requested)


if __name__ == "__main__":
    unittest.main()
