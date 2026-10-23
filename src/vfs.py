"""In-memory snapshot of a host directory, used as the VFS."""

import os
from dataclasses import dataclass, field
from pathlib import Path


class VirtualFileSystemError(ValueError):
    """Represent an invalid VFS path or filesystem operation."""


@dataclass
class Node:
    """Directory or file fully stored inside process memory."""

    is_directory: bool
    children: dict = field(default_factory=dict)
    data: bytes = b""


class VirtualFileSystem:
    """Read a directory snapshot without changing its disk contents."""

    def __init__(self, root):
        """Read the host tree once, without unpacking or modifying it."""
        path = Path(root)
        if not path.is_dir():
            raise VirtualFileSystemError(f"Каталог VFS не найден: {path}")
        try:
            self.root = self._snapshot(path)
        except OSError as error:
            message = f"Ошибка чтения VFS: {error}"
            raise VirtualFileSystemError(message) from error
        self._cwd = []

    @staticmethod
    def _snapshot(path):
        """Recursively copy regular files and directories to memory."""
        node = Node(is_directory=True)
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    node.children[entry.name] = VirtualFileSystem._snapshot(
                        Path(entry.path),
                    )
                elif entry.is_file(follow_symlinks=False):
                    data = Path(entry.path).read_bytes()
                    node.children[entry.name] = Node(False, data=data)
        return node

    @property
    def cwd(self):
        """Report the current directory using UNIX path separators."""
        return "/" + "/".join(self._cwd)

    def _parts(self, path):
        """Resolve '.', '..', absolute paths and relative paths."""
        parts = [] if path.startswith("/") else self._cwd.copy()
        for part in path.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        return parts

    def _node(self, parts):
        """Find an item by its already normalized name components."""
        node = self.root
        for part in parts:
            if not node.is_directory:
                raise VirtualFileSystemError("Это не каталог")
            if part not in node.children:
                pathname = "/" + "/".join(parts)
                raise VirtualFileSystemError(f"Путь не найден: {pathname}")
            node = node.children[part]
        return node

    def list_directory(self, path="."):
        """Return names in a directory or the name of one file."""
        parts = self._parts(path)
        node = self._node(parts)
        if not node.is_directory:
            return [parts[-1]]
        return sorted(node.children)

    def change_directory(self, path="/"):
        """Change the in-memory working directory."""
        parts = self._parts(path)
        if not self._node(parts).is_directory:
            raise VirtualFileSystemError("это не каталог")
        self._cwd = parts

    def mkdir(self, path):
        """Create one directory only in the snapshot, never on disk."""
        name = path.rstrip("/").split("/")[-1]
        if not name or name in (".", ".."):
            raise VirtualFileSystemError("некорректное имя каталога")
        parts = self._parts(path)
        parent = self._node(parts[:-1])
        if not parent.is_directory:
            raise VirtualFileSystemError("родитель не каталог")
        if name in parent.children:
            raise VirtualFileSystemError("такой файл или каталог уже есть")
        parent.children[name] = Node(is_directory=True)
