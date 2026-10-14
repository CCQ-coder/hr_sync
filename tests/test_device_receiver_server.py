"""Integration tests for the asyncio raw TCP listener."""

from __future__ import annotations

import asyncio
import ipaddress
import json
import logging
import tempfile
import unittest
from pathlib import Path

from device_raw_receiver.config import ReceiverConfig

try:
    from device_raw_receiver.server import RawTcpServer
except ImportError as import_error:  # TDD: server absence is an assertion failure.
    SERVER_IMPORT_ERROR = import_error
    RawTcpServer = None
else:
    SERVER_IMPORT_ERROR = None


class RawTcpServerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.storage_root = Path(self.temporary_directory.name) / "receiver-data"
        self.logger = logging.getLogger("device_raw_receiver.tests")
        previous_propagate = self.logger.propagate
        self.logger.propagate = False
        self.addCleanup(setattr, self.logger, "propagate", previous_propagate)
        handler = logging.NullHandler()
        self.logger.addHandler(handler)
        self.addCleanup(self.logger.removeHandler, handler)
        self.servers = []

    async def asyncTearDown(self) -> None:
        for server in reversed(self.servers):
            await server.stop()

    def make_config(self, **overrides: object) -> ReceiverConfig:
        values: dict[str, object] = {
            "listen_host": "127.0.0.1",
            "tcp_port": 0,
            "storage_root": self.storage_root,
            "allowed_networks": (ipaddress.ip_network("127.0.0.0/8"),),
            "segment_max_bytes": 64,
            "read_buffer_bytes": 8,
            "idle_timeout_seconds": 0,
            "fsync_policy": "always",
            "max_connections": 2,
            "minimum_free_bytes": 0,
        }
        values.update(overrides)
        return ReceiverConfig(**values)

    async def start_server(self, **overrides: object) -> "RawTcpServer":
        self.assertIsNone(SERVER_IMPORT_ERROR, f"server module is unavailable: {SERVER_IMPORT_ERROR}")
        server = RawTcpServer(self.make_config(**overrides), self.logger)
        await server.start()
        self.servers.append(server)
        return server

    async def wait_for_metadata(self, root: Path, status: str = None) -> Path:
        for _ in range(100):
            paths = list(root.glob("incoming/*/*/*/*/session.json"))
            if paths:
                if status is None:
                    return paths[0]
                metadata = json.loads(paths[0].read_text(encoding="utf-8"))
                if metadata["status"] == status:
                    return paths[0]
            await asyncio.sleep(0.01)
        self.fail("session metadata did not reach the expected state")

    async def test_multiple_writes_without_disconnect_stay_one_session(self) -> None:
        server = await self.start_server()
        reader, writer = await asyncio.open_connection("127.0.0.1", server.bound_port)
        writer.write(b"first")
        await writer.drain()
        writer.write(b"second")
        await writer.drain()

        await self.wait_for_metadata(self.storage_root, "open")
        self.assertEqual(1, len(list(self.storage_root.glob("incoming/*/*/*/*/session.json"))))
        writer.close()
        await writer.wait_closed()

        metadata_path = await self.wait_for_metadata(self.storage_root, "closed")
        payloads = sorted(metadata_path.parent.glob("payload-*.bin"))
        self.assertEqual(b"firstsecond", b"".join(path.read_bytes() for path in payloads))
        self.assertEqual(b"", await reader.read())

    async def test_idle_connection_is_saved_with_idle_timeout_status(self) -> None:
        server = await self.start_server(idle_timeout_seconds=1)
        reader, writer = await asyncio.open_connection("127.0.0.1", server.bound_port)

        metadata_path = await self.wait_for_metadata(self.storage_root, "idle_timeout")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(0, metadata["total_bytes"])
        self.assertEqual(b"", await reader.read())
        writer.close()
        await writer.wait_closed()

    async def test_unapproved_source_is_closed_without_session_directory(self) -> None:
        server = await self.start_server(allowed_networks=(ipaddress.ip_network("192.168.10.0/24"),))
        reader, writer = await asyncio.open_connection("127.0.0.1", server.bound_port)

        self.assertEqual(b"", await reader.read())
        await asyncio.sleep(0.05)
        self.assertEqual([], list(self.storage_root.glob("incoming/*/*/*/*/session.json")))
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    unittest.main()
