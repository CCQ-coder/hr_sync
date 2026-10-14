"""Create a clean, allowlisted QMS ERP release directory.

This script intentionally never reads or copies qms_erp_sync_config.json or
qms_erp_sync_state.json from the shared dist directory.  It is invoked by the
PowerShell build script before and after PyInstaller runs.
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from typing import Iterable, Optional, Set, Tuple


class ReleasePackageError(RuntimeError):
    """The release directory is unsafe to overwrite or a required source is missing."""


SAFE_EXE_NAME = re.compile(r"^[A-Za-z0-9_\-\u4e00-\u9fff]+$")
WINDOWS_RESERVED_BASENAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{number}" for number in range(1, 10)}
    | {f"LPT{number}" for number in range(1, 10)}
)


def validate_executable_name(exe_name: object) -> str:
    """Accept only a strict Windows-safe EXE base name before making paths."""
    if not isinstance(exe_name, str) or not exe_name or exe_name != exe_name.strip():
        raise ReleasePackageError("可执行文件名称不安全：必须是非空、无首尾空白的文件名。")
    if "/" in exe_name or "\\" in exe_name or ".." in exe_name:
        raise ReleasePackageError("可执行文件名称不安全：不得包含绝对路径、分隔符或路径遍历。")
    if not SAFE_EXE_NAME.fullmatch(exe_name) or exe_name.upper() in WINDOWS_RESERVED_BASENAMES:
        raise ReleasePackageError("可执行文件名称不安全：只允许英文、数字、下划线、连字符和中文安全字符。")
    return exe_name


def release_directory(dist: Path, exe_name: str) -> Path:
    exe_name = validate_executable_name(exe_name)
    return Path(dist) / f"{exe_name}-发布包"


def release_artifacts(exe_name: str) -> Tuple[Tuple[str, str], ...]:
    """Return (source-relative-path, release-filename) pairs for safe delivery."""
    exe_name = validate_executable_name(exe_name)
    return (
        (f"dist/{exe_name}.exe", f"{exe_name}.exe"),
        ("erp_field_registry.json", "erp_field_registry.json"),
        ("outputs/erp_field_rename_manifest.json", "erp_field_rename_manifest.json"),
        ("sql/erp_field_rename_preflight.sql", "erp_field_rename_preflight.sql"),
        ("sql/erp_field_rename_apply.sql", "erp_field_rename_apply.sql"),
        ("sql/erp_field_rename_verify.sql", "erp_field_rename_verify.sql"),
        ("sql/erp_field_rename_contract.sql", "erp_field_rename_contract.sql"),
        ("qms_erp_raw_schema.sql", "qms_erp_raw_schema.sql"),
        ("qms_erp_sync_config.example.json", "qms_erp_sync_config.example.json"),
    )


def allowed_release_filenames(exe_name: str) -> Set[str]:
    return {destination for _, destination in release_artifacts(exe_name)}


def _unexpected_release_entries(directory: Path, allowed: Set[str]) -> Iterable[str]:
    if not directory.exists():
        return ()
    if not directory.is_dir():
        return (directory.name,)
    unexpected = []
    for entry in directory.rglob("*"):
        relative = entry.relative_to(directory)
        if entry.is_symlink() or entry.is_dir() or len(relative.parts) != 1 or entry.name not in allowed:
            unexpected.append(relative.as_posix())
    return tuple(sorted(unexpected))


def validate_release_directory(directory: Path, exe_name: str) -> Path:
    """Reject a polluted release directory without changing any of its contents."""
    exe_name = validate_executable_name(exe_name)
    directory = Path(directory)
    unexpected = tuple(_unexpected_release_entries(directory, allowed_release_filenames(exe_name)))
    if unexpected:
        names = ", ".join(unexpected)
        raise ReleasePackageError(
            f"发布目录包含意外文件或目录，拒绝复制以避免泄露敏感配置：{directory} / {names}"
        )
    return directory


def stage_release_package(root: Path, dist: Path, exe_name: str) -> Path:
    """Copy only the explicit safe allowlist into a versioned release directory."""
    exe_name = validate_executable_name(exe_name)
    root = Path(root)
    dist = Path(dist)
    directory = validate_release_directory(release_directory(dist, exe_name), exe_name)
    artifacts = release_artifacts(exe_name)
    sources = [(root / relative, destination) for relative, destination in artifacts]
    missing = [str(source) for source, _ in sources if not source.is_file()]
    if missing:
        raise ReleasePackageError("缺少发布文件，拒绝创建不完整发布包：" + "; ".join(missing))

    directory.mkdir(parents=True, exist_ok=True)
    for source, destination in sources:
        shutil.copy2(source, directory / destination)
    validate_release_directory(directory, exe_name)
    return directory


def parse_arguments(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a clean allowlisted ERP release directory.")
    parser.add_argument("--root", required=True, help="Project root directory")
    parser.add_argument("--dist", required=True, help="Shared PyInstaller dist directory")
    parser.add_argument("--exe-name", required=True, help="Executable base name without .exe")
    parser.add_argument("--validate-only", action="store_true", help="Only reject a polluted release directory")
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> int:
    arguments = parse_arguments(argv)
    try:
        exe_name = validate_executable_name(arguments.exe_name)
        directory = release_directory(Path(arguments.dist), exe_name)
        if arguments.validate_only:
            validate_release_directory(directory, exe_name)
            print(f"发布目录安全检查通过：{directory}")
        else:
            staged = stage_release_package(Path(arguments.root), Path(arguments.dist), exe_name)
            print(f"已生成仅含白名单文件的发布包：{staged}")
        return 0
    except ReleasePackageError as exc:
        print(f"发布包拒绝：{exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
