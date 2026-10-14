"""Async TCP listener that persists every received byte before notification."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Callable, Optional, Set

from .archive import SessionArchive
from .config import ReceiverConfig
from .models import PersistedChunk, SessionStatus


PersistedCallback = Callable[[PersistedChunk], None]


class RawTcpServer:
    """A configurable TCP listener with no protocol parsing layer."""

    def __init__(
        self,
        config: ReceiverConfig,
        logger: logging.Logger,
        on_persisted: Optional[PersistedCallback] = None,
    ) -> None:
        self._config = config
        self._logger = logger
        self._on_persisted = on_persisted
        self._server: Optional[asyncio.base_events.Server] = None
        self._slots = asyncio.Semaphore(config.max_connections)
        self._connection_tasks: Set[asyncio.Task] = set()
        self._writers: Set[asyncio.StreamWriter] = set()

    @property
    def bound_port(self) -> int:
        """Return the actual port after the listener has started."""
        if self._server is None or not self._server.sockets:
            raise RuntimeError("TCP 服务尚未启动")
        return int(self._server.sockets[0].getsockname()[1])

    async def start(self) -> None:
        """Bind the listener using the validated address and port."""
        if self._server is not None:
            raise RuntimeError("TCP 服务已启动")
        self._server = await asyncio.start_server(
            self._handle_connection,
            host=self._config.listen_host,
            port=self._config.tcp_port,
        )
        self._logger.info("TCP 接收服务已监听 %s:%s", self._config.listen_host, self.bound_port)

    async def stop(self) -> None:
        """Stop accepting connections and close every active writer."""
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        for writer in tuple(self._writers):
            writer.close()
        if self._connection_tasks:
            await asyncio.gather(*tuple(self._connection_tasks), return_exceptions=True)
        self._logger.info("TCP 接收服务已停止")

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        task = asyncio.current_task()
        if task is not None:
            self._connection_tasks.add(task)
        self._writers.add(writer)
        try:
            peer = writer.get_extra_info("peername")
            local = writer.get_extra_info("sockname")
            if not peer or not local:
                self._logger.warning("拒绝缺少地址信息的 TCP 连接")
                return
            peer_host, peer_port = str(peer[0]), int(peer[1])
            local_host, local_port = str(local[0]), int(local[1])
            if not self._config.allows(peer_host):
                self._logger.warning("拒绝非白名单来源 %s:%s", peer_host, peer_port)
                return
            if self._slots.locked():
                self._logger.warning("拒绝连接，已达到并发上限: %s:%s", peer_host, peer_port)
                return

            async with self._slots:
                archive = SessionArchive.create(
                    self._config.storage_root,
                    local_host,
                    local_port,
                    peer_host,
                    peer_port,
                    self._config.segment_max_bytes,
                    self._config.fsync_policy,
                )
                await self._receive_stream(reader, archive)
        except Exception as error:
            self._logger.exception("TCP 连接处理失败: %s", error)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except (ConnectionError, OSError):
                pass
            self._writers.discard(writer)
            if task is not None:
                self._connection_tasks.discard(task)

    async def _receive_stream(self, reader: asyncio.StreamReader, archive: SessionArchive) -> None:
        try:
            while True:
                if self._config.idle_timeout_seconds:
                    data = await asyncio.wait_for(
                        reader.read(self._config.read_buffer_bytes),
                        timeout=self._config.idle_timeout_seconds,
                    )
                else:
                    data = await reader.read(self._config.read_buffer_bytes)
                if not data:
                    archive.close(SessionStatus.CLOSED)
                    return
                chunk = archive.append(data)
                self._notify_persisted(chunk)
        except asyncio.TimeoutError:
            archive.close(SessionStatus.IDLE_TIMEOUT, "idle_timeout")
        except Exception as error:
            try:
                archive.close(SessionStatus.CLOSED_ABNORMALLY, type(error).__name__)
            except Exception:
                self._logger.exception("无法完成异常会话归档: %s", archive.session_id)
            raise

    def _notify_persisted(self, chunk: PersistedChunk) -> None:
        if self._on_persisted is None:
            return
        try:
            self._on_persisted(chunk)
        except Exception:
            self._logger.exception("处理器回调失败，会话 %s 不受影响", chunk.session_id)
