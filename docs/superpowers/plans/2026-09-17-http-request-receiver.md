# HTTP Request Receiver Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone, token-protected HTTP service on port 3100 that archives each accepted HTTP request to disk.

**Architecture:** A standard-library package validates the JSON configuration, accepts requests using a threaded HTTP server, authenticates `X-Receiver-Token`, and delegates persistence to an atomic archive function. Each accepted request receives an isolated timestamped directory with structured metadata and byte-exact body data.

**Tech Stack:** Python 3.10+, standard library (`http.server`, `hmac`, `hashlib`, `json`, `uuid`, `pathlib`), `unittest`.

**Spec:** `docs/superpowers/specs/2026-09-17-http-request-receiver-design.md`

## Global Constraints

- Use only Python 3 standard-library runtime dependencies.
- Bind the configured `0.0.0.0:3100`; never hard-code a deployment path or a real secret.
- Require a 32-character-or-longer `receiver_token` and compare it to the sole `X-Receiver-Token` with `hmac.compare_digest`.
- Archive only authenticated requests that are at most `max_body_bytes`; preserve their body unchanged in `body.bin`.
- Remove `X-Receiver-Token` from stored metadata and never emit request headers or bodies into the application log.
- Place every accepted request in `<storage_root>/requests/YYYY/MM/DD/<request-id>/` with `request.json` and `body.bin`.
- Reply with `201`, `401`, `413`, or `500` as defined by the specification.

---

### Task 1: Validated receiver configuration

**Files:**
- Create: `http_request_receiver/__init__.py`
- Create: `http_request_receiver/config.py`
- Create: `http_request_receiver_config.example.json`
- Test: `tests/test_http_request_receiver_config.py`

**Interfaces:**
- Produces: `HttpReceiverConfig(listen_host: str, port: int, storage_root: Path, receiver_token: str, max_body_bytes: int)`.
- Produces: `load_config(path: Path) -> HttpReceiverConfig` and `ConfigError(ValueError)`.

- [ ] **Step 1: Write the failing test**

```python
config = load_config(config_path)
self.assertEqual("0.0.0.0", config.listen_host)
self.assertEqual(3100, config.port)
with self.assertRaises(ConfigError):
    load_config(path_with_receiver_token("short"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_http_request_receiver_config -v`

Expected: FAIL because the module does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
@dataclass(frozen=True)
class HttpReceiverConfig:
    listen_host: str
    port: int
    storage_root: Path
    receiver_token: str
    max_body_bytes: int

def load_config(path: Path) -> HttpReceiverConfig:
    """Read and validate the complete JSON receiver configuration."""
```

Parse a UTF-8 JSON object. Reject missing keys, non-IP listener values, ports outside 1–65535, empty/temporary storage roots, tokens shorter than 32 characters, and non-positive limits. Add a JSON example using port 3100 and a placeholder secret.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_http_request_receiver_config -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add http_request_receiver/__init__.py http_request_receiver/config.py http_request_receiver_config.example.json tests/test_http_request_receiver_config.py
git commit -m "feat: add HTTP receiver configuration"
```

### Task 2: Atomic request archive with secret redaction

**Files:**
- Create: `http_request_receiver/archive.py`
- Test: `tests/test_http_request_receiver_archive.py`

**Interfaces:**
- Produces: `ArchivedRequest(request_id: str, directory: Path)`.
- Produces: `archive_request(storage_root: Path, method: str, target: str, full_url: str, headers: Sequence[tuple[str, str]], body: bytes, peer_host: str, peer_port: int, received_at: datetime) -> ArchivedRequest`.

- [ ] **Step 1: Write the failing test**

```python
archived = archive_request(root, "POST", "/events?source=test", "http://receiver.example:3100/events?source=test",
    [("Content-Type", "application/json"), ("X-Receiver-Token", "secret")],
    b'{"device":"a"}', "203.0.113.9", 40001, utc_now)
metadata = json.loads((archived.directory / "request.json").read_text())
self.assertEqual(b'{"device":"a"}', (archived.directory / "body.bin").read_bytes())
self.assertNotIn("X-Receiver-Token", [name for name, _ in metadata["headers"]])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_http_request_receiver_archive -v`

Expected: FAIL because `archive_request` does not exist.

- [ ] **Step 3: Write minimal implementation**

Create the date directory and a same-parent temporary request directory. Write `body.bin` and a UTF-8 `request.json` with request ID, UTC timestamp, method, target, supplied full URL, peer, ordered non-secret headers, byte count and SHA-256. Publish the completed request directory with `os.replace`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_http_request_receiver_archive -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add http_request_receiver/archive.py tests/test_http_request_receiver_archive.py
git commit -m "feat: archive HTTP requests"
```

### Task 3: Authenticated HTTP server

**Files:**
- Create: `http_request_receiver/server.py`
- Test: `tests/test_http_request_receiver_server.py`

**Interfaces:**
- Consumes: `HttpReceiverConfig`.
- Produces: `HttpRequestReceiverServer(config: HttpReceiverConfig, logger: logging.Logger)`, `start() -> None`, `stop() -> None`, and `bound_port: int`.

- [ ] **Step 1: Write the failing test**

```python
response = self.request("PATCH", "/hooks/device?type=raw", b"\x00payload\xff",
    {"X-Receiver-Token": self.token})
self.assertEqual(201, response.status)
self.assertEqual(b"\x00payload\xff", self.only_archive_body())
self.assertEqual(401, self.request("POST", "/hooks", b"discard", {}).status)
self.assertEqual([], list(self.storage_root.glob("requests/*/*/*/*")))
```

Include separate tests for `GET` with an empty saved body, duplicated non-secret headers retained in order, a duplicated token header rejected, a declared oversize body rejected before reading, and a chunked body exceeding the limit rejected without an archive.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_http_request_receiver_server -v`

Expected: FAIL because the server module does not exist.

- [ ] **Step 3: Write minimal implementation**

Use `ThreadingHTTPServer` with handlers for `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, and `OPTIONS` delegated to one method. Verify exactly one token header with `hmac.compare_digest`, support bounded content-length and chunked-body reading, construct the full URL from the received `Host` header and unmodified path, then call `archive_request`. Return compact JSON containing only the request ID. Log only status and request ID.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_http_request_receiver_server -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add http_request_receiver/server.py tests/test_http_request_receiver_server.py
git commit -m "feat: add authenticated HTTP receiver"
```

### Task 4: Command-line service and secure deployment guide

**Files:**
- Create: `http_request_receiver/main.py`
- Create: `run_http_request_receiver.py`
- Create: `README_http_request_receiver.md`
- Test: `tests/test_http_request_receiver_cli.py`

**Interfaces:**
- Consumes: `python run_http_request_receiver.py --config /etc/http-request-receiver/config.json`.
- Produces: exit code `2` for invalid configuration and a server process that stops cleanly on SIGINT/SIGTERM.

- [ ] **Step 1: Write the failing test**

```python
def test_run_returns_two_when_config_is_missing(self) -> None:
    self.assertEqual(2, run(["--config", str(self.temporary_path / "missing.json")]))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_http_request_receiver_cli -v`

Expected: FAIL because `http_request_receiver.main` does not exist.

- [ ] **Step 3: Write minimal implementation**

Implement `run(argv: Optional[Sequence[str]] = None) -> int`, start the configured server, and install signal handlers where available. Document a 1Panel-ready systemd deployment: create a non-root user, create an external archive directory, lock the config to mode 600, create a long random token, start the service, open port 3100 only to necessary sources, and verify with `curl`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_http_request_receiver_cli -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add http_request_receiver/main.py run_http_request_receiver.py README_http_request_receiver.md tests/test_http_request_receiver_cli.py
git commit -m "docs: add HTTP receiver deployment guide"
```

### Task 5: Regression verification

**Files:**
- Modify: `README_http_request_receiver.md`
- Test: `tests/test_http_request_receiver_config.py`
- Test: `tests/test_http_request_receiver_archive.py`
- Test: `tests/test_http_request_receiver_server.py`
- Test: `tests/test_http_request_receiver_cli.py`

**Interfaces:**
- Consumes: all modules and the documented port-3100 deployment command.
- Produces: verified request archival behaviour and accurate operator instructions.

- [ ] **Step 1: Write the failing test**

```python
response = self.request("POST", "/capture?a=1&b=%E4%B8%AD", b"value")
metadata = self.only_archive_metadata()
self.assertEqual("/capture?a=1&b=%E4%B8%AD", metadata["target"])
self.assertNotIn("X-Receiver-Token", [name for name, _ in metadata["headers"]])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests -p 'test_http_request_receiver_*.py' -v`

Expected: FAIL until the server passes the unmodified path-and-query target into the archive.

- [ ] **Step 3: Write minimal implementation**

Pass the received `self.path` without normalization to `archive_request`; correct any deployment instructions that do not use port 3100 or `X-Receiver-Token`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests -p 'test_http_request_receiver_*.py' -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README_http_request_receiver.md tests/test_http_request_receiver_server.py
git commit -m "test: verify HTTP request archive contract"
```
