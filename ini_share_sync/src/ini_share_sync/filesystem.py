"""Small filesystem helpers that also work with Python 3.4 on Windows XP."""

import os


def ensure_directory(path):
    """Create *path* and its parents, accepting an already existing directory."""
    try:
        os.makedirs(str(path))
    except OSError:
        if not path.is_dir():
            raise


def read_text(path, encoding):
    """Read text without relying on methods added to pathlib after Python 3.4."""
    with open(str(path), "r", encoding=encoding) as handle:
        return handle.read()


def write_text(path, content, encoding):
    """Write text without relying on methods added to pathlib after Python 3.4."""
    with open(str(path), "w", encoding=encoding) as handle:
        handle.write(content)
