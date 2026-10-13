# 局域网 INI 文件定时同步 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 Windows 设备上每 5 分钟将 `D:\WTD\JOBS` 第一层任务目录内的同名 INI 文件可靠复制为 UNC 共享目录中设备编号子目录下的 TXT 文件。

**Architecture:** 在 `D:\project\hr_sync\ini_share_sync` 新建一个独立的纯 Python 项目。一次性 CLI 负责加载 JSON 配置、发现候选文件、以 SHA-256 识别变更、原子传输至共享目录并保存本地状态；Windows 计划任务只负责每五分钟唤起该 CLI。PowerShell 脚本将计划任务名称固定为 `IniShareSync`，并提供幂等的安装与删除操作。

**Tech Stack:** Python 3.8+ 标准库（`pathlib`、`hashlib`、`json`、`logging`、`shutil`、`msvcrt`）、`unittest`、PowerShell 5.1+、PyInstaller（仅用于打包可选 EXE）。

**Spec:** `D:\project\hr_sync\docs\superpowers\specs\2026-09-15-ini-share-sync-design.md`

## Global Constraints

- 所有实现文件必须位于 `D:\project\hr_sync\ini_share_sync`，不得修改现有 QMS/ERP 同步工具。
- 仅处理 `source_root` 第一层子目录的 `<job_name>\<job_name>.ini`；不递归扫描。
- 目标路径必须是 `target_root\device_id\<job_name>.txt`，内容字节保持原样。
- `device_id` 必须是单层安全目录名；禁止空字符串、`.`、`..`、反斜杠、正斜杠、冒号及 NUL。
- 首次全量同步；后续以 SHA-256 指纹仅同步新增或内容改变的源文件。
- 源端删除绝不删除远端 TXT 或同步状态；只有成功上传后才写入状态。
- 目标端写入必须先落临时文件，再以替换操作发布正式 TXT。
- 任务固定名为 `IniShareSync`，间隔 5 分钟，使用可写入 `\\Scbgx\数字化` 的当前 Windows 登录账户，且忽略重叠实例。
- 必须兼容 Python 3.8：不使用 `list[str]`、`X | Y` 或其它 Python 3.9+ 语法。

---

## File Structure

```text
D:\project\hr_sync\ini_share_sync\
├── src\ini_share_sync\
│   ├── __init__.py                 # Package marker and version.
│   ├── config.py                   # JSON configuration and validation.
│   ├── discovery.py                # First-level job-directory discovery.
│   ├── state.py                    # SHA-256 and atomic local state persistence.
│   ├── transfer.py                 # Atomic copy from INI to target TXT.
│   ├── locking.py                  # Windows non-blocking single-instance file lock.
│   └── main.py                     # CLI orchestration, exit codes and logging.
├── tests\
│   ├── __init__.py
│   ├── test_config_and_discovery.py
│   ├── test_state_and_transfer.py
│   └── test_main.py
├── sync_config.json                # Deployable configuration, initially requires device_id edit.
├── sync_config.example.json        # Recovery/example configuration.
├── run_ini_share_sync.py            # Thin development/EXE entry point for the package CLI.
├── install_sync_task.ps1           # Create/replace the named 5-minute task.
├── remove_sync_task.ps1            # Idempotently remove only that named task.
├── build_exe.ps1                   # Build dist\IniShareSync.exe from main.py.
└── README.md                       # Deployment, permissions and operating instructions.
```

### Task 1: Create the isolated project, configuration, and candidate discovery

**Files:**
- Create: `D:\project\hr_sync\ini_share_sync\src\ini_share_sync\__init__.py`
- Create: `D:\project\hr_sync\ini_share_sync\src\ini_share_sync\config.py`
- Create: `D:\project\hr_sync\ini_share_sync\src\ini_share_sync\discovery.py`
- Create: `D:\project\hr_sync\ini_share_sync\tests\__init__.py`
- Create: `D:\project\hr_sync\ini_share_sync\tests\test_config_and_discovery.py`
- Create: `D:\project\hr_sync\ini_share_sync\sync_config.json`
- Create: `D:\project\hr_sync\ini_share_sync\sync_config.example.json`

**Interfaces:**
- Produces `SyncConfig(source_root: Path, target_root: Path, device_id: str)` and `load_config(config_path: Path) -> SyncConfig`.
- Produces `SyncCandidate(job_name: str, source_path: Path)` and `find_candidates(source_root: Path) -> List[SyncCandidate]`.
- Later tasks use a candidate's `job_name` to form `<target_root>/<device_id>/<job_name>.txt`.

- [ ] **Step 1: Write the failing configuration and discovery tests**

```python
from pathlib import Path
import json
import tempfile
import unittest

from ini_share_sync.config import ConfigError, load_config
from ini_share_sync.discovery import find_candidates


class ConfigAndDiscoveryTests(unittest.TestCase):
    def test_load_config_returns_paths_and_device_id(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sync_config.json"
            path.write_text(json.dumps({
                "source_root": r"D:\WTD\JOBS",
                "target_root": r"\\Scbgx\数字化\飞针机",
                "device_id": "FEIZHEN-01",
            }), encoding="utf-8")

            config = load_config(path)

        self.assertEqual(Path("D:/WTD/JOBS"), config.source_root)
        self.assertEqual("FEIZHEN-01", config.device_id)

    def test_load_config_rejects_device_id_that_can_escape_target_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sync_config.json"
            path.write_text(json.dumps({
                "source_root": r"D:\WTD\JOBS",
                "target_root": r"\\Scbgx\数字化\飞针机",
                "device_id": r"..\other-device",
            }), encoding="utf-8")

            with self.assertRaises(ConfigError):
                load_config(path)

    def test_find_candidates_checks_only_first_level_matching_ini_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "p2l046433a"
            valid.mkdir()
            (valid / "p2l046433a.INI").write_bytes(b"valid")
            invalid = root / "different-name"
            invalid.mkdir()
            (invalid / "other.ini").write_bytes(b"ignore")
            nested = valid / "nested"
            nested.mkdir()
            (nested / "nested.ini").write_bytes(b"ignore")

            candidates = find_candidates(root)

        self.assertEqual(["p2l046433a"], [item.job_name for item in candidates])
        self.assertEqual("p2l046433a.INI", candidates[0].source_path.name)
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
$env:PYTHONPATH = "$PWD\src"; python -m unittest tests.test_config_and_discovery -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'ini_share_sync'`.

- [ ] **Step 3: Implement minimal configuration and discovery logic**

```python
# src/ini_share_sync/config.py
import json
from dataclasses import dataclass
from pathlib import Path


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class SyncConfig:
    source_root: Path
    target_root: Path
    device_id: str


def load_config(config_path: Path) -> SyncConfig:
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8-sig"))
        source_root = Path(raw["source_root"])
        target_root = Path(raw["target_root"])
        device_id = str(raw["device_id"]).strip()
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ConfigError("无法读取有效的 sync_config.json") from exc
    if not device_id or device_id in (".", "..") or any(ch in device_id for ch in "\\\\/:\\x00"):
        raise ConfigError("device_id 必须是安全的单层目录名")
    return SyncConfig(source_root=source_root, target_root=target_root, device_id=device_id)
```

```python
# src/ini_share_sync/discovery.py
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class SyncCandidate:
    job_name: str
    source_path: Path


def find_candidates(source_root: Path) -> List[SyncCandidate]:
    candidates = []
    for child in sorted(source_root.iterdir(), key=lambda item: item.name.casefold()):
        if not child.is_dir():
            continue
        matching = [
            path for path in child.iterdir()
            if path.is_file()
            and path.suffix.casefold() == ".ini"
            and path.stem.casefold() == child.name.casefold()
        ]
        if matching:
            candidates.append(SyncCandidate(child.name, sorted(matching)[0]))
    return candidates
```

Create both configuration JSON files with the approved paths and an obvious placeholder `"device_id": "请填写设备编号"`. Add `"__version__ = \"1.0.0\""` to `__init__.py`.

- [ ] **Step 4: Run the focused test to verify it passes**

Run:

```powershell
$env:PYTHONPATH = "$PWD\src"; python -m unittest tests.test_config_and_discovery -v
```

Expected: PASS with three tests.

- [ ] **Step 5: Commit**

This workspace is not a Git repository. Do not run `git commit`; record that this self-contained task has passed its focused test.

### Task 2: Add file fingerprints, persistent state, and atomic TXT transfer

**Files:**
- Create: `D:\project\hr_sync\ini_share_sync\src\ini_share_sync\state.py`
- Create: `D:\project\hr_sync\ini_share_sync\src\ini_share_sync\transfer.py`
- Create: `D:\project\hr_sync\ini_share_sync\tests\test_state_and_transfer.py`

**Interfaces:**
- Consumes `SyncCandidate` from `discovery.py`.
- Produces `sha256_file(path: Path) -> str`, `load_state(path: Path) -> Dict[str, Dict[str, str]]`, `save_state(path: Path, entries: Dict[str, Dict[str, str]]) -> None`, and `candidate_key(candidate: SyncCandidate) -> str`.
- Produces `target_path(config: SyncConfig, candidate: SyncCandidate) -> Path` and `copy_as_txt(source_path: Path, destination_path: Path) -> None`.
- `main.py` will copy only when `state[candidate_key(candidate)]["sha256"] != sha256_file(candidate.source_path)` and will update state only after `copy_as_txt` returns the digest of the bytes it published.

- [ ] **Step 1: Write the failing state and atomic-copy tests**

```python
from pathlib import Path
import tempfile
import unittest

from ini_share_sync.config import SyncConfig
from ini_share_sync.discovery import SyncCandidate
from ini_share_sync.state import candidate_key, load_state, save_state, sha256_file
from ini_share_sync.transfer import copy_as_txt, target_path


class StateAndTransferTests(unittest.TestCase):
    def test_state_round_trip_and_hash_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "job.ini"
            source.write_bytes(b"first")
            candidate = SyncCandidate("job", source)
            first_hash = sha256_file(source)
            state_path = root / "sync_state.json"
            save_state(state_path, {candidate_key(candidate): first_hash})
            source.write_bytes(b"changed")

            state = load_state(state_path)

        self.assertEqual(first_hash, state[candidate_key(candidate)])
        self.assertNotEqual(state[candidate_key(candidate)], sha256_file(source))

    def test_copy_as_txt_preserves_bytes_and_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "p2l.ini"
            payload = "[job]\r\nvalue=中文\r\n".encode("utf-8")
            source.write_bytes(payload)
            config = SyncConfig(root, root / "share", "FEIZHEN-01")
            destination = target_path(config, SyncCandidate("p2l", source))

            copy_as_txt(source, destination)

            self.assertEqual(payload, destination.read_bytes())
            self.assertEqual("p2l.txt", destination.name)
            self.assertEqual([], list(destination.parent.glob("*.part")))
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
$env:PYTHONPATH = "$PWD\src"; python -m unittest tests.test_state_and_transfer -v
```

Expected: FAIL with `ModuleNotFoundError` for `ini_share_sync.state`.

- [ ] **Step 3: Implement fingerprint, state persistence, and atomic copy**

```python
# src/ini_share_sync/state.py
import hashlib
import json
import os
from pathlib import Path
from typing import Dict

from .discovery import SyncCandidate


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def candidate_key(candidate: SyncCandidate) -> str:
    return str(candidate.source_path.resolve()).casefold()


def load_state(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("files", {}), dict):
        raise ValueError("sync_state.json 格式无效")
    return {str(key): str(value) for key, value in raw["files"].items()}


def save_state(path: Path, entries: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps({"files": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(str(temporary), str(path))
```

```python
# src/ini_share_sync/transfer.py
import os
import shutil
import uuid
from pathlib import Path

from .config import SyncConfig
from .discovery import SyncCandidate


def target_path(config: SyncConfig, candidate: SyncCandidate) -> Path:
    return config.target_root / config.device_id / (candidate.job_name + ".txt")


def copy_as_txt(source_path: Path, destination_path: Path) -> None:
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination_path.with_name(
        "." + destination_path.name + "." + uuid.uuid4().hex + ".part"
    )
    try:
        shutil.copyfile(str(source_path), str(temporary))
        os.replace(str(temporary), str(destination_path))
    finally:
        if temporary.exists():
            temporary.unlink()
```

- [ ] **Step 4: Run the focused test to verify it passes**

Run:

```powershell
$env:PYTHONPATH = "$PWD\src"; python -m unittest tests.test_state_and_transfer -v
```

Expected: PASS with two tests.

- [ ] **Step 5: Commit**

This workspace is not a Git repository. Do not run `git commit`; record that this self-contained task has passed its focused test.

### Task 3: Implement the one-shot CLI, logging, and no-overlap guard

**Files:**
- Create: `D:\project\hr_sync\ini_share_sync\src\ini_share_sync\locking.py`
- Create: `D:\project\hr_sync\ini_share_sync\src\ini_share_sync\main.py`
- Create: `D:\project\hr_sync\ini_share_sync\run_ini_share_sync.py`
- Create: `D:\project\hr_sync\ini_share_sync\tests\test_main.py`

**Interfaces:**
- Consumes `load_config`, `find_candidates`, `sha256_file`, `load_state`, `save_state`, `candidate_key`, `target_path`, and `copy_as_txt` from Tasks 1–2.
- Produces `run_sync(config_path: Path, application_dir: Path) -> int` and `main(argv: Optional[Sequence[str]] = None) -> int`.
- Exit codes: `0` = no errors, `1` = configuration/state/source-root failure, `2` = one or more file transfer failures, `3` = another run currently holds the lock.

- [ ] **Step 1: Write the failing orchestration tests**

```python
from pathlib import Path
import json
import tempfile
import unittest

from ini_share_sync.main import run_sync


class MainTests(unittest.TestCase):
    def write_config(self, root):
        config_path = root / "sync_config.json"
        config_path.write_text(json.dumps({
            "source_root": str(root / "source"),
            "target_root": str(root / "target"),
            "device_id": "FEIZHEN-01",
        }), encoding="utf-8")
        return config_path

    def test_first_run_copies_then_second_run_skips_and_change_recopies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            job = root / "source" / "p2l046433a"
            job.mkdir(parents=True)
            source = job / "p2l046433a.ini"
            source.write_bytes(b"one")
            config_path = self.write_config(root)

            self.assertEqual(0, run_sync(config_path, root))
            target = root / "target" / "FEIZHEN-01" / "p2l046433a.txt"
            self.assertEqual(b"one", target.read_bytes())
            first_mtime = target.stat().st_mtime_ns
            self.assertEqual(0, run_sync(config_path, root))
            self.assertEqual(first_mtime, target.stat().st_mtime_ns)
            source.write_bytes(b"two")
            self.assertEqual(0, run_sync(config_path, root))
            self.assertEqual(b"two", target.read_bytes())

    def test_deleted_source_does_not_delete_existing_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            job = root / "source" / "job"
            job.mkdir(parents=True)
            source = job / "job.ini"
            source.write_bytes(b"persist")
            config_path = self.write_config(root)
            self.assertEqual(0, run_sync(config_path, root))
            source.unlink()

            self.assertEqual(0, run_sync(config_path, root))

            self.assertEqual(b"persist", (root / "target" / "FEIZHEN-01" / "job.txt").read_bytes())
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
$env:PYTHONPATH = "$PWD\src"; python -m unittest tests.test_main -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'ini_share_sync.main'`.

- [ ] **Step 3: Implement the lock and orchestration**

```python
# src/ini_share_sync/locking.py
import msvcrt
from pathlib import Path


class SingleRunLock:
    def __init__(self, path: Path):
        self.path = path
        self.handle = None

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+b")
        self.handle.seek(0)
        if not self.handle.read(1):
            self.handle.seek(0)
            self.handle.write(b"0")
            self.handle.flush()
        self.handle.seek(0)
        try:
            msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            self.handle.close()
            self.handle = None
            return False

    def release(self) -> None:
        if self.handle is not None:
            self.handle.seek(0)
            msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            self.handle.close()
            self.handle = None
```

```python
# src/ini_share_sync/main.py
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Sequence

from .config import ConfigError, load_config
from .discovery import find_candidates
from .locking import SingleRunLock
from .state import candidate_key, load_state, save_state, sha256_file
from .transfer import copy_as_txt, target_path


def build_logger(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("ini_share_sync")
    logger.setLevel(logging.INFO)
    logger.handlers[:] = []
    handler = logging.FileHandler(
        str(log_dir / ("sync-" + datetime.now().strftime("%Y-%m-%d") + ".log")),
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def run_sync(config_path: Path, application_dir: Path) -> int:
    logger = build_logger(application_dir / "logs")
    lock = SingleRunLock(application_dir / "ini_share_sync.lock")
    if not lock.acquire():
        logger.warning("已有同步实例正在运行，本次跳过")
        return 3
    try:
        config = load_config(config_path)
        if not config.source_root.is_dir():
            raise ConfigError("source_root 不存在或不是目录")
        state_path = application_dir / "sync_state.json"
        state = load_state(state_path)
        failures = 0
        for candidate in find_candidates(config.source_root):
            fingerprint = sha256_file(candidate.source_path)
            key = candidate_key(candidate)
            if state.get(key) == fingerprint:
                logger.info("未变化，跳过：%s", candidate.source_path)
                continue
            try:
                copy_as_txt(candidate.source_path, target_path(config, candidate))
                state[key] = fingerprint
                save_state(state_path, state)
                logger.info("同步成功：%s", candidate.source_path)
            except OSError as exc:
                failures += 1
                logger.error("同步失败：%s；%s", candidate.source_path, exc)
        return 2 if failures else 0
    except (ConfigError, OSError, ValueError) as exc:
        logger.error("本轮未执行：%s", exc)
        return 1
    finally:
        lock.release()


def runtime_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="同步同名 INI 到局域网共享目录")
    parser.add_argument("--config", type=Path)
    arguments = parser.parse_args(argv)
    app_dir = runtime_directory()
    return run_sync(arguments.config or app_dir / "sync_config.json", app_dir)
```

Create the exact thin entry point below. It makes package-relative imports work both in development and under PyInstaller:

```python
# run_ini_share_sync.py
from ini_share_sync.main import main


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the focused test to verify it passes**

Run:

```powershell
$env:PYTHONPATH = "$PWD\src"; python -m unittest tests.test_main -v
```

Expected: PASS with two tests.

- [ ] **Step 5: Run the full Python suite**

Run:

```powershell
$env:PYTHONPATH = "$PWD\src"; python -m unittest discover -s tests -v
```

Expected: PASS with all Task 1–3 tests.

- [ ] **Step 6: Commit**

This workspace is not a Git repository. Do not run `git commit`; record the full-suite result in the final handoff.

### Task 4: Add EXE packaging, 5-minute task installation/removal, and operational documentation

**Files:**
- Create: `D:\project\hr_sync\ini_share_sync\build_exe.ps1`
- Create: `D:\project\hr_sync\ini_share_sync\install_sync_task.ps1`
- Create: `D:\project\hr_sync\ini_share_sync\remove_sync_task.ps1`
- Create: `D:\project\hr_sync\ini_share_sync\README.md`
- Modify: `D:\project\hr_sync\ini_share_sync\tests\test_main.py`

**Interfaces:**
- Consumes `src\ini_share_sync\main.py` as the PyInstaller entry point.
- Produces `dist\IniShareSync.exe`, called by the `IniShareSync` task action.
- Produces fixed-name installer and uninstaller scripts for `IniShareSync`; the scripts must not operate on unrelated task names.

- [ ] **Step 1: Write the failing packaging and script-content tests**

```python
def test_task_scripts_use_the_approved_task_name_and_five_minute_interval(self):
    project_root = Path(__file__).resolve().parents[1]
    installer = (project_root / "install_sync_task.ps1").read_text(encoding="utf-8")
    remover = (project_root / "remove_sync_task.ps1").read_text(encoding="utf-8")

    self.assertIn('"IniShareSync"', installer)
    self.assertIn('New-TimeSpan -Minutes 5', installer)
    self.assertIn('IgnoreNew', installer)
    self.assertIn('Unregister-ScheduledTask', remover)
    self.assertIn('"IniShareSync"', remover)
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
$env:PYTHONPATH = "$PWD\src"; python -m unittest tests.test_main.MainTests.test_task_scripts_use_the_approved_task_name_and_five_minute_interval -v
```

Expected: FAIL because the PowerShell files do not yet exist.

- [ ] **Step 3: Implement the scripts and README**

`build_exe.ps1` must invoke the active Python interpreter's PyInstaller module with this exact command structure; the `run_ini_share_sync.py` entry point is required so the package's relative imports continue to work in the EXE:

```powershell
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSCommandPath
$python = (Get-Command python -ErrorAction Stop).Source
$entryPoint = Join-Path $projectRoot "run_ini_share_sync.py"
& $python -m PyInstaller --noconfirm --clean --onefile --name IniShareSync `
    --paths (Join-Path $projectRoot "src") `
    --distpath (Join-Path $projectRoot "dist") `
    --workpath (Join-Path $projectRoot "build") `
    --specpath (Join-Path $projectRoot "build") $entryPoint
if ($LASTEXITCODE -ne 0) { throw "PyInstaller 打包失败，退出码：$LASTEXITCODE" }
```

`install_sync_task.ps1` must use these concrete elements:

```powershell
param([string]$TaskName = "IniShareSync")

$projectRoot = Split-Path -Parent $PSCommandPath
$exePath = Join-Path $projectRoot "dist\IniShareSync.exe"
if (-not (Test-Path -LiteralPath $exePath)) {
    throw "未找到 $exePath。请先运行 .\build_exe.ps1。"
}
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) `
    -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable
$action = New-ScheduledTaskAction -Execute $exePath -WorkingDirectory $projectRoot
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $currentUser `
    -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Settings $settings -Principal $principal -Force | Out-Null
```

`remove_sync_task.ps1` must set the same default task name and be safe to run repeatedly:

```powershell
param([string]$TaskName = "IniShareSync")

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($null -ne $existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "已删除计划任务：$TaskName"
} else {
    Write-Host "计划任务不存在：$TaskName"
}
```

README must include exact commands for: editing `sync_config.json`; setting the real device number; manual development run with `$env:PYTHONPATH = "$PWD\src"; python -m ini_share_sync.main`; building; installing the task; removing the task; reading `logs`; and the requirement that the logged-in account can create/write `\\Scbgx\数字化\飞针机\<device_id>`.

- [ ] **Step 4: Run the focused script-content test to verify it passes**

Run:

```powershell
$env:PYTHONPATH = "$PWD\src"; python -m unittest tests.test_main.MainTests.test_task_scripts_use_the_approved_task_name_and_five_minute_interval -v
```

Expected: PASS.

- [ ] **Step 5: Run all verification checks**

Run:

```powershell
$env:PYTHONPATH = "$PWD\src"; python -m unittest discover -s tests -v
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
Test-Path .\dist\IniShareSync.exe
```

Expected: all unit tests PASS, build exits `0`, and the final command returns `True`. Do not install the actual scheduled task or write to `\\Scbgx\数字化\飞针机` during automated verification; that requires the destination machine's account permissions and is an operator action.

- [ ] **Step 6: Commit**

This workspace is not a Git repository. Do not run `git commit`; report the completed file set and verification output instead.

## Plan Self-Review

- **Spec coverage:** Tasks 1–3 cover first-level same-name discovery, config safety, SHA-256 first/full/incremental behavior, target mapping, no-delete handling, atomic transfer, state-after-success, logging, error exit codes, and instance locking. Task 4 covers EXE build, task creation, 5-minute interval, overlap suppression, idempotent removal, and operations documentation.
- **Placeholder scan:** The plan has no unresolved placeholders or unspecified test steps. Each implementation task provides exact files, signatures, test commands, and concrete code/PowerShell elements.
- **Type consistency:** `SyncConfig`, `SyncCandidate`, `candidate_key`, `target_path`, and `run_sync` are introduced before later tasks consume them. All Python syntax remains Python 3.8 compatible.
