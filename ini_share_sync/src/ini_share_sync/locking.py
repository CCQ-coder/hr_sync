"""A small Windows file lock used to avoid overlapping scheduled runs."""

import msvcrt
from pathlib import Path

from .filesystem import ensure_directory


class SingleRunLock:
    """Hold a non-blocking one-byte Windows lock until :meth:`release` is called."""

    def __init__(self, path):
        self.path = path
        self._handle = None

    def acquire(self):
        ensure_directory(self.path.parent)
        self._handle = self.path.open("a+b")
        self._handle.seek(0)
        try:
            msvcrt.locking(self._handle.fileno(), msvcrt.LK_NBLCK, 1)
            self._handle.seek(0)
            if not self._handle.read(1):
                self._handle.seek(0)
                self._handle.write(b"0")
                self._handle.flush()
            return True
        except OSError:
            self._handle.close()
            self._handle = None
            return False

    def release(self):
        if self._handle is None:
            return
        try:
            self._handle.seek(0)
            msvcrt.locking(self._handle.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            self._handle.close()
            self._handle = None
