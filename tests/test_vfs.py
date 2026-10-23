"""Tests for an in-memory directory snapshot."""

import tempfile
import unittest
from pathlib import Path

from src.vfs import VirtualFileSystem, VirtualFileSystemError


class VirtualFileSystemTests(unittest.TestCase):
    """Test the snapshot, path resolution and no-disk-write rule."""

    def setUp(self):
        """Create a temporary directory tree for each test."""
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "one" / "two").mkdir(parents=True)
        (self.root / "one" / "two" / "file.txt").write_text("first")
        self.vfs = VirtualFileSystem(self.root)

    def tearDown(self):
        """Remove only temporary test fixtures."""
        self.temp.cleanup()

    def test_deep_tree(self):
        """Keep files several levels below the VFS root."""
        names = self.vfs.list_directory("/one/two")
        self.assertEqual(names, ["file.txt"])

    def test_snapshot_ignores_later_disk_changes(self):
        """Do not reload modified host files after initial snapshot."""
        (self.root / "new.txt").write_text("later")
        self.assertEqual(self.vfs.list_directory("/"), ["one"])

    def test_paths(self):
        """Resolve relative paths and parent traversals."""
        self.vfs.change_directory("one/two")
        self.assertEqual(self.vfs.cwd, "/one/two")
        self.vfs.change_directory("..")
        self.assertEqual(self.vfs.cwd, "/one")

    def test_mkdir_changes_memory_not_disk(self):
        """Create a VFS directory without touching the physical source."""
        self.vfs.mkdir("/one/new")
        self.assertIn("new", self.vfs.list_directory("one"))
        self.assertFalse((self.root / "one/new").exists())

    def test_mkdir_nested(self):
        """Create a second directory inside one made in memory."""
        self.vfs.mkdir("/one/new")
        self.vfs.mkdir("/one/new/sub")
        self.assertEqual(self.vfs.list_directory("/one/new"), ["sub"])

    def test_mkdir_errors(self):
        """Reject existing items and missing parents."""
        with self.assertRaises(VirtualFileSystemError):
            self.vfs.mkdir("/one")
        with self.assertRaises(VirtualFileSystemError):
            self.vfs.mkdir("/missing/child")
        with self.assertRaises(VirtualFileSystemError):
            self.vfs.mkdir("/")

    def test_missing_path(self):
        """Report a nonexistent virtual path."""
        with self.assertRaises(VirtualFileSystemError):
            self.vfs.list_directory("/nothing")


if __name__ == "__main__":
    unittest.main()
