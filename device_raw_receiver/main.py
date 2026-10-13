"""Command-line entry point for the raw TCP receiver."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import shutil
import signal
import sys
import uuid
from pathlib import Path
from typing import Optional, Sequence

from .archive import recover_open_sessions
from .config import ConfigError, ReceiverConfig, load_config
from .logging_setup import configure_application_logger
from .server import RawTcpServer


class _WindowSafeArgumentParser(argparse.ArgumentParser):
    """Avoid argparse writing to absent streams in a windowed executable."""

    def error(self, message: str) -> None:
        raise ConfigError("命令行参数错误: {0}".format(message))

    def _print_message(self, message: Optional[str], file=None) -> None:
        if not message:
            return
        output = file if file is not None else getattr(sys, "stdout", None)
        if output is None or not hasattr(output, "write"):
            return
        try:
            output.write(message)
        except (OSError, ValueError):
            return


def run(argv: Optional[Sequence[str]] = None) -> int:
    """Validate configuration and run until the process receives a stop signal."""
    application_directory = _application_directory()
    parser = _WindowSafeArgumentParser(description="局域网设备原始 TCP 数据接收服务")
    parser.add_argument(
        "--config",
        type=Path,
        default=application_directory / "device_receiver_config.json",
        help="接收器 JSON 配置文件路径；默认为程序同目录的 device_receiver_config.json",
    )
    try:
        arguments = parser.parse_args(argv)
        config = load_config(arguments.config)
        _validate_storage(config)
    except ConfigError as error:
        _report_startup_error("配置错误: {0}".format(error), application_directory)
        return 2

    logger = configure_application_logger(config.storage_root)
    try:
        asyncio.run(_serve(config, logger))
    except KeyboardInterrupt:
        logger.info("收到键盘中断，接收服务停止")
        return 0
    except Exception:
        logger.exception("接收服务启动或运行失败")
        return 1
    return 0


def _application_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def _report_startup_error(message: str, application_directory: Path) -> None:
    output = getattr(sys, "stderr", None)
    if output is not None and hasattr(output, "write"):
        try:
            output.write(message + "\n")
            output.flush()
            return
        except (OSError, ValueError):
            pass

    try:
        with (application_directory / "startup-error.log").open("a", encoding="utf-8") as error_log:
            error_log.write(message + "\n")
    except OSError:
        pass


async def _serve(config: ReceiverConfig, logger: logging.Logger) -> None:
    recovered = recover_open_sessions(config.storage_root)
    if recovered:
        logger.warning("已标记 %s 个未完成会话为 interrupted", len(recovered))
    server = RawTcpServer(config, logger)
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for stop_signal in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(stop_signal, stop_event.set)
        except (NotImplementedError, RuntimeError):
            pass
    await server.start()
    try:
        await stop_event.wait()
    finally:
        await server.stop()


def _validate_storage(config: ReceiverConfig) -> None:
    try:
        config.storage_root.mkdir(parents=True, exist_ok=True)
        probe_path = config.storage_root / ".receiver-write-{0}.probe".format(uuid.uuid4())
        with probe_path.open("xb") as probe:
            probe.write(b"ok")
            probe.flush()
            os.fsync(probe.fileno())
        probe_path.unlink()
        available_bytes = shutil.disk_usage(config.storage_root).free
    except OSError as error:
        raise ConfigError("storage_root 无法创建或写入") from error
    if available_bytes < config.minimum_free_bytes:
        raise ConfigError("storage_root 可用磁盘空间低于 minimum_free_bytes")


if __name__ == "__main__":
    raise SystemExit(run())
