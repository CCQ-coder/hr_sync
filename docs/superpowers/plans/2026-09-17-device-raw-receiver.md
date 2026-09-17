# 标特福设备原始数据接收服务 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 Windows 10 上部署一个可配置的 TCP 后台接收器，完整归档局域网设备连接中的原始字节流，并为后续解析/API 留下稳定边界。

**Architecture:** 独立包 `device_raw_receiver` 仅依赖 Python 标准库。`config` 验证监听和来源限制；`archive` 持久化会话的原始分卷和元数据；`server` 负责 asyncio TCP 生命周期；`main` 负责 CLI、启动恢复和日志。落盘后只发布不可变 `PersistedChunk`，首版没有外部处理器。

**Tech Stack:** Python 3.8+、`asyncio`、`unittest`、PyInstaller、`schtasks.exe`、PowerShell。

**Spec:** `docs/superpowers/specs/2026-09-17-device-raw-receiver-design.md`

## Global Constraints

- 首版只支持 TCP；不实现 FTP、UDP、HTTP、`.rot` 解析、数据库写入或外部 API。
- 不把一次 `recv`、超时或分卷边界视为业务请求边界。
- `payload-*.bin` 只能二进制写入，不能插入、转码、压缩、去重、截断或重写。
- `idle_timeout_seconds: 0` 禁用空闲超时；无白名单配置时拒绝启动。
- 只使用标准库和项目既有的 `unittest`；部署包不含实际配置或已接收数据。
- 每个任务在测试通过后创建一个本地 Git 提交。

---

## File Structure

| Path | Responsibility |
| --- | --- |
| `device_raw_receiver/config.py` | JSON 配置、CIDR/端口/目录验证。 |
| `device_raw_receiver/models.py` | 会话状态和不可变落盘事件。 |
| `device_raw_receiver/archive.py` | 原始分卷、JSONL 审计、摘要和恢复。 |
| `device_raw_receiver/server.py` | TCP 监听、白名单、并发和连接状态。 |
| `device_raw_receiver/logging_setup.py` | UTF-8 按日滚动日志。 |
| `device_raw_receiver/main.py` | CLI、磁盘检查、恢复和优雅停止。 |
| `tests/test_device_receiver_*.py` | 配置、归档、恢复、TCP 和部署测试。 |
| `DeviceRawReceiver.spec` and `*.ps1` | 打包、计划任务安装和删除。 |

### Task 1: Initialize Git and configuration validation

**Files:**

- Create: `.gitignore`, `device_raw_receiver/__init__.py`, `device_raw_receiver/config.py`
- Create: `tests/test_device_receiver_config.py`, `device_receiver_config.example.json`
- Modify: `requirements.txt`

**Interfaces:** Produces `ConfigError`, `load_config(path: Path) -> ReceiverConfig`, and `ReceiverConfig.allows(address: str) -> bool`.

- [ ] **Step 1: Initialize the local repository**

Run `git init`, then set repository-local identity with `git config user.name "Codex"` and `git config user.email "codex@local"`. Add `.venv/`, `__pycache__/`, `build/`, `dist/`, `device_receiver_config.json`, `device_raw_receiver_data/`, and `logs/` to `.gitignore`.

- [ ] **Step 2: Write failing configuration tests**

```python
def test_loads_explicit_tcp_listener(self):
    config = load_config(self.write_json({
        "listen_host": "0.0.0.0", "tcp_port": 9100,
        "storage_root": str(self.root / "data"),
        "allowed_networks": ["192.168.10.0/24"],
        "segment_max_bytes": 16, "read_buffer_bytes": 8,
        "idle_timeout_seconds": 0, "fsync_policy": "always",
        "max_connections": 2, "minimum_free_bytes": 0,
    }))
    self.assertTrue(config.allows("192.168.10.55"))
    self.assertFalse(config.allows("192.168.11.55"))

def test_rejects_empty_source_whitelist(self):
    with self.assertRaisesRegex(ConfigError, "allowed_networks"):
        load_config(self.write_json(self.valid_config(allowed_networks=[])))
```

Cover invalid/out-of-range ports, an invalid CIDR, non-positive segment/buffer size, unsupported fsync policy, negative timeout, and listener `0.0.0.0` without a CIDR.

- [ ] **Step 3: Verify failure**

Run: `python -m unittest tests.test_device_receiver_config -v`

Expected: FAIL because `device_raw_receiver.config` is absent.

- [ ] **Step 4: Implement and verify configuration**

```python
@dataclass(frozen=True)
class ReceiverConfig:
    listen_host: str
    tcp_port: int
    storage_root: Path
    allowed_networks: Tuple[Union[ipaddress.IPv4Network, ipaddress.IPv6Network], ...]
    segment_max_bytes: int = 64 * 1024 * 1024
    read_buffer_bytes: int = 64 * 1024
    idle_timeout_seconds: int = 0
    fsync_policy: str = "always"
    max_connections: int = 16
    minimum_free_bytes: int = 1024 * 1024 * 1024

    def allows(self, address: str) -> bool: ...
```

Use `json.loads`, `ipaddress.ip_network(..., strict=False)`, `Path.resolve()` and explicit type/range checks; reject missing keys and paths equal to `tempfile.gettempdir()` or its direct child. Template uses port 9100, `D:\\DeviceRawReceiverData`, CIDR `192.168.10.0/24`, and no secrets. Run `python -m unittest tests.test_device_receiver_config -v`; expected PASS.

- [ ] **Step 5: Commit**

Run `git add .gitignore requirements.txt device_raw_receiver tests/test_device_receiver_config.py device_receiver_config.example.json` and `git commit -m "feat: add receiver configuration validation"`.

### Task 2: Persist byte-exact session archives

**Files:**

- Create: `device_raw_receiver/models.py`, `device_raw_receiver/archive.py`, `tests/test_device_receiver_archive.py`

**Interfaces:** Consumes `ReceiverConfig`. Produces `SessionArchive.create(...)`, `append(data: bytes) -> PersistedChunk`, `close(status, reason=None)`, and `recover_open_sessions(storage_root) -> list[str]`.

- [ ] **Step 1: Write failing archive tests**

```python
def test_preserves_binary_and_gbk_bytes(self):
    archive = self.new_archive(segment_max_bytes=64)
    archive.append(b"\x00A")
    archive.append("中文".encode("gbk"))
    archive.append(b"\xff")
    archive.close(SessionStatus.CLOSED)
    payload = b"".join(p.read_bytes() for p in self.payloads(archive))
    self.assertEqual(b"\x00A" + "中文".encode("gbk") + b"\xff", payload)
    self.assertEqual("closed", self.metadata(archive)["status"])
```

Add the `segment_max_bytes=3` case: append `b"abcd"`, then `b"ef"`; assert the files contain `b"abcd"` then `b"ef"`. Assert ordered concatenation, SHA-256, event offsets/lengths and no raw bytes in `events.jsonl`.

- [ ] **Step 2: Verify failure**

Run: `python -m unittest tests.test_device_receiver_archive -v`

Expected: FAIL because `archive` and `models` are absent.

- [ ] **Step 3: Implement archive writer**

```python
class SessionStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    CLOSED_ABNORMALLY = "closed_abnormally"
    IDLE_TIMEOUT = "idle_timeout"
    INTERRUPTED = "interrupted"

@dataclass(frozen=True)
class PersistedChunk:
    session_id: str
    segment_name: str
    offset: int
    length: int
    path: Path

class SessionArchive:
    @classmethod
    def create(cls, storage_root, local_host, local_port, peer_host, peer_port,
               segment_max_bytes, fsync_policy): ...
    def append(self, data: bytes) -> PersistedChunk: ...
    def close(self, status: SessionStatus, reason: Optional[str] = None) -> None: ...
```

Use UTC `incoming/YYYY/MM/DD/<uuid>/`, `payload-%06d.bin`, incremental SHA-256, JSON Lines with `ensure_ascii=False`, and `os.replace()` for `session.json`. `always` flushes and fsyncs each append; `on_close` fsyncs at segment switch and close. A buffer is never split: create a new segment before the next append after the prior segment reaches its threshold.

- [ ] **Step 4: Verify and commit**

Run `python -m unittest tests.test_device_receiver_archive -v`; expected PASS. Then run `git add device_raw_receiver/models.py device_raw_receiver/archive.py tests/test_device_receiver_archive.py` and `git commit -m "feat: archive raw tcp session bytes"`.

### Task 3: Recover interrupted sessions without touching payloads

**Files:**

- Modify: `device_raw_receiver/archive.py`, `tests/test_device_receiver_archive.py`

**Interfaces:** `recover_open_sessions(storage_root)` returns only IDs changed from `open` to `interrupted`; it never writes a payload file.

- [ ] **Step 1: Write failing recovery tests**

```python
archive = self.new_archive()
archive.append(b"before-crash")
before = {p.name: p.read_bytes() for p in self.payloads(archive)}
self.assertEqual([archive.session_id], recover_open_sessions(self.storage_root))
self.assertEqual(before, {p.name: p.read_bytes() for p in self.payloads(archive)})
self.assertEqual("interrupted", self.metadata(archive)["status"])
```

Also prove a closed session is skipped and corrupt `session.json` logs an error while every payload is byte-identical.

- [ ] **Step 2: Verify failure**

Run: `python -m unittest tests.test_device_receiver_archive.SessionRecoveryTests -v`

Expected: FAIL because recovery does not yet write the `interrupted` state.

- [ ] **Step 3: Implement and verify recovery**

Scan only `incoming/*/*/*/session.json`; parse valid `open` metadata; sort only `payload-\d{6}.bin`; re-hash by streaming; append a `recovered` event; atomically set status, `ended_at`, `total_bytes`, segments and digest. Catch per-session errors and continue. Run `python -m unittest tests.test_device_receiver_archive -v`; expected PASS.

- [ ] **Step 4: Commit**

Run `git add device_raw_receiver/archive.py tests/test_device_receiver_archive.py` and `git commit -m "feat: recover interrupted raw sessions"`.

### Task 4: Run the asyncio TCP listener safely

**Files:**

- Create: `device_raw_receiver/server.py`, `device_raw_receiver/logging_setup.py`, `tests/test_device_receiver_server.py`

**Interfaces:** Consumes `ReceiverConfig`, `SessionArchive`, `SessionStatus`, and `PersistedChunk`. Produces `RawTcpServer(config, logger, on_persisted=None)`, async `start()`/`stop()`, and `bound_port`. `on_persisted` is `Callable[[PersistedChunk], None]`.

- [ ] **Step 1: Write failing async tests**

```python
async def test_multiple_writes_without_disconnect_stay_one_session(self):
    reader, writer = await asyncio.open_connection("127.0.0.1", self.server.bound_port)
    writer.write(b"first")
    await writer.drain()
    writer.write(b"second")
    await writer.drain()
    await self.wait_for_open_session()
    self.assertEqual(1, len(self.session_json_paths()))
    writer.close()
    await writer.wait_closed()
    self.assertEqual(b"firstsecond", self.read_single_payload())
```

Use `unittest.IsolatedAsyncioTestCase`. Add tests for a positive idle timeout (`idle_timeout` state), correct callback offset/length, blocked `::1` against an IPv4-only CIDR (skip when unavailable), and `max_connections=1` refusing a second client while preserving the first session.

- [ ] **Step 2: Verify failure**

Run: `python -m unittest tests.test_device_receiver_server -v`

Expected: FAIL because `RawTcpServer` is absent.

- [ ] **Step 3: Implement logging and TCP lifecycle**

Implement `configure_application_logger(storage_root: Path) -> logging.Logger` with an UTF-8 daily `TimedRotatingFileHandler` in `<storage_root>/logs` and no raw payload data.

Implement `RawTcpServer` with `asyncio.start_server`. Before `SessionArchive.create`, compare peer IP with `config.allows`; write rejections only to the application log. Use `asyncio.Semaphore(config.max_connections)`. Read with `reader.read(config.read_buffer_bytes)`, wrapped with `asyncio.wait_for` only when timeout is positive. `b""` gives `closed`; `TimeoutError` gives `idle_timeout`; I/O errors give `closed_abnormally`. Call the callback only after `archive.append` succeeds; log callback errors without interrupting storage. Close/wait for the writer in `finally`.

- [ ] **Step 4: Verify and commit**

Run `python -m unittest tests.test_device_receiver_server -v`; expected PASS. Then run `git add device_raw_receiver/server.py device_raw_receiver/logging_setup.py tests/test_device_receiver_server.py` and `git commit -m "feat: receive and persist tcp connections"`.

### Task 5: Package and install as a Windows background program

**Files:**

- Create: `device_raw_receiver/main.py`, `DeviceRawReceiver.spec`, `build_device_raw_receiver.ps1`
- Create: `install_device_raw_receiver_task.ps1`, `remove_device_raw_receiver_task.ps1`, `README_device_raw_receiver.md`
- Modify: `tests/test_device_receiver_config.py`

**Interfaces:** `main.run(argv: Optional[Sequence[str]] = None) -> int`; exit 0 only after clean stop, 2 for invalid configuration, and 1 for startup/runtime failure. Scheduled task name defaults to `DeviceRawReceiver` and runs as `SYSTEM` at startup.

- [ ] **Step 1: Write failing CLI and deployment tests**

```python
def test_missing_config_returns_usage_error(self):
    self.assertEqual(2, run(["--config", str(self.root / "missing.json")]))

def test_installer_uses_startup_system_task_and_whatif(self):
    script = (ROOT / "install_device_raw_receiver_task.ps1").read_text("utf-8")
    self.assertIn("schtasks.exe", script)
    self.assertIn("/SC ONSTART", script)
    self.assertIn("/RU SYSTEM", script)
    self.assertIn("SupportsShouldProcess", script)
```

Add a test for a non-writable storage root before port binding and static checks that the removal script only targets `DeviceRawReceiver` with `ShouldProcess`.

- [ ] **Step 2: Verify failure**

Run: `python -m unittest tests.test_device_receiver_config -v`

Expected: FAIL because `main` and deployment scripts are absent.

- [ ] **Step 3: Implement CLI, packaging and task scripts**

`main.run` uses `argparse`, `load_config`, creation/write validation of `storage_root`, `shutil.disk_usage` against `minimum_free_bytes`, recovery before listener start, `asyncio.run`, and SIGINT/SIGTERM where available. It logs paths/errors but not raw bytes.

The PyInstaller spec has `console=False`, entry point `device_raw_receiver/main.py`, executable name `DeviceRawReceiver`, and no embedded config/data. The build script creates `dist/DeviceRawReceiver` through an explicit allowlist of EXE, configuration template, README and the two scripts; it fails if `device_receiver_config.json` is present.

The installer has `CmdletBinding(SupportsShouldProcess)`, validates EXE and actual config, then creates only `DeviceRawReceiver` with `schtasks.exe /Create /SC ONSTART /RU SYSTEM /RL HIGHEST`. It never creates/overwrites the actual config. The remover validates its task name and runs the corresponding `schtasks.exe /Delete` only after `ShouldProcess`.

README documents controlled-folder deployment, copying/renaming the template, the required port/CIDR, elevated task install, a manually-created firewall rule limited to the CIDR, log inspection, recovery semantics and non-goals.

- [ ] **Step 4: Verify package and commit**

Run `python -m unittest discover -s tests -p "test_device_receiver_*.py" -v`; expected PASS. Run `powershell -ExecutionPolicy Bypass -File .\build_device_raw_receiver.ps1`; expected clean `dist\DeviceRawReceiver\DeviceRawReceiver.exe` with no actual config or `payload-*.bin`. Then run `git add device_raw_receiver DeviceRawReceiver.spec build_device_raw_receiver.ps1 install_device_raw_receiver_task.ps1 remove_device_raw_receiver_task.ps1 README_device_raw_receiver.md tests/test_device_receiver_config.py` and `git commit -m "feat: package windows raw tcp receiver"`.

### Task 6: Regression and handoff verification

**Files:** Modify `README_device_raw_receiver.md` only if verification exposes an instruction mismatch.

**Interfaces:** Consumes all receiver components; produces clean local Git history and a verified deployment package.

- [ ] **Step 1: Run complete receiver regression**

Run `python -m unittest discover -s tests -p "test_device_receiver_*.py" -v`; expected PASS for config, archive, recovery, TCP and deployment tests.

- [ ] **Step 2: Run existing-project regression**

Run `python -m unittest discover -s tests -p "test_*.py" -v`; expected PASS. If an existing external dependency fails, report exact test/error and do not modify unrelated ERP code.

- [ ] **Step 3: Inspect source control and release files**

Run `git status --short`, `git log --oneline -6`, and `Get-ChildItem dist\DeviceRawReceiver -File`. Expected: receiver commits exist; package omits `device_receiver_config.json` and all raw payloads.

- [ ] **Step 4: Commit a documentation correction only if required**

If a correction was made, run `git add README_device_raw_receiver.md` and `git commit -m "docs: verify raw receiver deployment"`; otherwise do not create an empty commit.

## Plan Self Review

| Spec requirement | Tasks |
| --- | --- |
| Configurable TCP, no invented request frame | 1 and 4 |
| Byte-for-byte original persistence, segments, metadata and SHA-256 | 2 |
| Crash recovery without payload mutation | 3 |
| CIDR, concurrency, idle and log safeguards | 1 and 4 |
| Future immutable processing event boundary | 2 and 4 |
| Windows EXE, startup task, firewall guidance | 5 |
| Tests, package inspection and regression | 1 through 6 |

No placeholder terms remain. All later interface names are defined in earlier tasks.
