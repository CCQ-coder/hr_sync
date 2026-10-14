"""Find the approved job INI files without descending into nested folders."""

from pathlib import Path


class SyncCandidate:
    """One approved source INI and its first-level job directory name."""

    def __init__(self, job_name, source_path):
        self.job_name = job_name
        self.source_path = source_path


def find_candidates(source_root):
    """Return one matching INI from each first-level job directory.

    A candidate is accepted only when a direct child directory contains a file
    whose stem matches the directory name and whose extension is `.ini`.
    """
    candidates = []
    children = sorted(source_root.iterdir(), key=lambda item: item.name.casefold())
    for child in children:
        if not child.is_dir():
            continue

        matches = [
            path
            for path in child.iterdir()
            if path.is_file()
            and path.suffix.casefold() == ".ini"
            and path.stem.casefold() == child.name.casefold()
        ]
        if matches:
            source_path = sorted(matches, key=lambda item: item.name.casefold())[0]
            candidates.append(SyncCandidate(job_name=child.name, source_path=source_path))
    return candidates
