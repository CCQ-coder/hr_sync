import base64
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import socket
import ssl
import sys
import tempfile
import threading
import types
import unittest
from unittest.mock import patch

from ini_share_sync.config import ConfigError, load_config
from ini_share_sync.discovery import SyncCandidate
from ini_share_sync.filesystem import write_text
from ini_share_sync import transfer


FIXTURES = Path(__file__).parent / "fixtures"


class UploadHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        self.server.requests.append((self.path, self.headers, body))
        self.send_response(self.server.response_status)
        self.end_headers()

    def log_message(self, *args):
        pass


class CloudTransferTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.server = HTTPServer(("127.0.0.1", 0), UploadHandler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(str(FIXTURES / "localhost-cert.pem"), str(FIXTURES / "localhost-key.pem"))
        self.server.socket = context.wrap_socket(self.server.socket, server_side=True)
        self.server.requests = []
        self.server.response_status = 204
        thread = threading.Thread(target=self.server.serve_forever)
        thread.daemon = True
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.raw = {
            "source_root": str(self.root / "source"),
            "server_url": "https://localhost:" + str(self.server.server_port),
            "device_id": "飞针机01",
            "upload_token": "test-device-token",
            "ca_cert": str(FIXTURES / "localhost-cert.pem"),
        }
        self.config_path = self.root / "sync_config.json"

    def config(self):
        write_text(self.config_path, json.dumps(self.raw), encoding="utf-8")
        return load_config(self.config_path)

    def candidate(self):
        source = self.root / "任务中文.ini"
        with source.open("wb") as handle:
            handle.write(b"[Test_Counters]\r\nraw=\x81\x40\r\n")
        return SyncCandidate("任务中文", source)

    def test_cloud_config_resolves_ca_relative_to_config_without_unc(self):
        self.raw["ca_cert"] = "ca.pem"
        with (self.root / "ca.pem").open("wb") as handle:
            handle.write((FIXTURES / "localhost-cert.pem").read_bytes())
        config = self.config()
        self.assertEqual(self.root / "ca.pem", config.ca_cert)
        self.assertIsNone(config.target_root)

    def test_rejects_insecure_or_incomplete_cloud_config(self):
        valid = self.raw.copy()
        for key, value in (("server_url", "http://example.com"), ("server_url", "https://user:pass@example.com"),
                           ("server_url", "https://example.com?token=x"), ("server_url", ""),
                           ("upload_token", "bad\r\nheader"), ("upload_token", ""), ("ca_cert", "missing.pem")):
            with self.subTest(key=key, value=value):
                self.raw = valid.copy()
                self.raw[key] = value
                with self.assertRaises(ConfigError):
                    self.config()

    def test_upload_preserves_bytes_utf8_metadata_and_legacy_filetimes(self):
        candidate = self.candidate()
        stat = candidate.source_path.stat()
        digest = transfer.upload_ini(self.config(), candidate)
        path, headers, body = self.server.requests[0]
        payload = json.loads(body.decode("utf-8"))
        self.assertEqual("/api/v1/flying-probe/device-files", path)
        self.assertEqual("test-device-token", headers["X-Device-Token"])
        self.assertIn("任务中文".encode("utf-8"), body)
        self.assertEqual({"schemaVersion", "deviceId", "jobName", "createdFileTime", "modifiedFileTime", "sha256", "contentBase64"}, set(payload))
        self.assertEqual("飞针机01", payload["deviceId"])
        self.assertEqual("任务中文", payload["jobName"])
        self.assertEqual(candidate.source_path.read_bytes(), base64.b64decode(payload["contentBase64"]))
        self.assertEqual(hashlib.sha256(candidate.source_path.read_bytes()).hexdigest(), digest)
        self.assertEqual(digest, payload["sha256"])
        self.assertEqual(int(round(stat.st_ctime * 10000000)) + 116444736000000000, payload["createdFileTime"])
        self.assertEqual(int(round(stat.st_mtime * 10000000)) + 116444736000000000, payload["modifiedFileTime"])

    def test_filetime_preserves_legacy_rounding_before_epoch_offset(self):
        value = transfer.timestamp_to_filetime(1700000000.123456)
        self.assertEqual(133444736001234560, (value.dwHighDateTime << 32) | value.dwLowDateTime)

    def test_non_2xx_is_failure_and_redirect_is_not_followed(self):
        candidate = self.candidate()
        for status in (302, 401, 413, 500):
            self.server.response_status = status
            with self.assertRaises(OSError):
                transfer.upload_ini(self.config(), candidate)
        self.assertEqual(4, len(self.server.requests))

    def test_tls_rejects_hostname_mismatch_and_untrusted_certificate(self):
        candidate = self.candidate()
        self.raw["server_url"] = self.raw["server_url"].replace("localhost", "127.0.0.1")
        with self.assertRaises(OSError):
            transfer.upload_ini(self.config(), candidate)
        self.raw["server_url"] = self.raw["server_url"].replace("127.0.0.1", "localhost")
        self.raw["ca_cert"] = ssl.get_default_verify_paths().cafile
        if self.raw["ca_cert"]:
            with self.assertRaises(OSError):
                transfer.upload_ini(self.config(), candidate)
        self.assertEqual([], self.server.requests)

    def test_upload_accepts_exactly_eight_mib_without_truncation(self):
        candidate = self.candidate()
        content = b"x" * 8388608
        with candidate.source_path.open("wb") as handle:
            handle.write(content)
        digest = transfer.upload_ini(self.config(), candidate)
        payload = json.loads(self.server.requests[0][2].decode("utf-8"))
        self.assertEqual(content, base64.b64decode(payload["contentBase64"]))
        self.assertEqual(hashlib.sha256(content).hexdigest(), digest)

    def test_changed_during_read_and_oversize_files_are_not_sent(self):
        candidate = self.candidate()
        config = self.config()
        original_stat = candidate.source_path.stat()
        changed_stat = type("ChangedStat", (), dict(st_size=0, st_mtime=0, st_ctime=0, st_ino=0))()
        with patch.object(Path, "stat", side_effect=[original_stat, changed_stat]):
            with self.assertRaises(ValueError):
                transfer.upload_ini(config, candidate)
        with candidate.source_path.open("wb") as handle:
            handle.write(b"x" * (8 * 1024 * 1024 + 1))
        with self.assertRaises(ValueError):
            transfer.upload_ini(self.config(), candidate)
        self.assertEqual([], self.server.requests)

    def test_cloud_retries_and_checkpoints_only_its_destination(self):
        if sys.platform == "win32":
            from ini_share_sync import main
        else:
            locking = types.ModuleType("ini_share_sync.locking")
            locking.SingleRunLock = type("TestLock", (), {
                "__init__": lambda self, path: None,
                "acquire": lambda self: True,
                "release": lambda self: None,
            })
            with patch.dict(sys.modules, {"ini_share_sync.locking": locking}):
                from ini_share_sync import main
        run_sync, run_host_status = main.run_sync, main.run_host_status
        source = self.root / "source" / "任务中文"
        source.mkdir(parents=True)
        with (source / "任务中文.ini").open("wb") as handle:
            handle.write(b"test")
        self.config()
        from ini_share_sync.state import candidate_key, save_state
        candidate = SyncCandidate("任务中文", source / "任务中文.ini")
        save_state(self.root / "sync_state.json", {candidate_key(candidate): {
            "sha256": hashlib.sha256(b"test").hexdigest(), "synced_at": "2026-11-01T00:00:00",
        }})
        legacy = (self.root / "sync_state.json").read_bytes()
        self.server.response_status = 401
        self.assertEqual(2, run_sync(self.config_path, self.root))
        self.assertFalse((self.root / "cloud_sync_state.json").exists())
        self.server.response_status = 204
        self.assertEqual(0, run_sync(self.config_path, self.root))
        self.assertEqual(0, run_sync(self.config_path, self.root))
        self.assertEqual(2, len(self.server.requests))
        self.assertEqual(legacy, (self.root / "sync_state.json").read_bytes())
        with patch("ini_share_sync.transfer.post_json", side_effect=socket.timeout("timeout")):
            self.raw["device_id"] = "飞针机02"
            self.config()
            self.assertEqual(2, run_sync(self.config_path, self.root))
        self.assertEqual(0, run_sync(self.config_path, self.root))
        self.raw["server_url"] += "/alternate"
        self.config()
        self.assertEqual(0, run_sync(self.config_path, self.root))
        self.assertEqual(4, len(self.server.requests))
        checkpoint = (self.root / "cloud_sync_state.json").read_bytes()
        sample = {"schemaVersion": 1, "deviceId": "飞针机02", "sampledAt": "2026-11-02T00:00:00Z"}
        with patch("ini_share_sync.main.capture_host_status", return_value=sample):
            with patch("ini_share_sync.main.find_candidates", side_effect=AssertionError("must not scan")):
                self.assertEqual(0, run_host_status(self.config_path, self.root))
            self.server.response_status = 401
            self.assertEqual(1, run_host_status(self.config_path, self.root))
        self.assertEqual(checkpoint, (self.root / "cloud_sync_state.json").read_bytes())
        self.assertEqual("/alternate/api/v1/flying-probe/device-host-status", self.server.requests[-1][0])
        self.assertEqual(sample, json.loads(self.server.requests[-1][2].decode("utf-8")))
        for log in (self.root / "logs").glob("*.log"):
            self.assertNotIn("test-device-token", log.read_bytes().decode("utf-8"))
