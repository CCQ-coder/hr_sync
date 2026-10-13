"""One-shot command-line synchroniser for device job files."""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from .config import ConfigError, load_config
from .discovery import find_candidates
from .filesystem import ensure_directory
from .locking import SingleRunLock
from .state import candidate_key, load_state, save_state, sha256_file
from .transfer import copy_as_txt, target_path


def build_logger(log_dir):
    """Create a per-day UTF-8 log file without retaining stale file handles."""
    ensure_directory(log_dir)
    logger = logging.getLogger("ini_share_sync")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    log_name = "sync-" + datetime.now().strftime("%Y-%m-%d") + ".log"
    handler = logging.FileHandler(str(log_dir / log_name), encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def close_logger(logger):
    """Close run-local log files so scheduled invocations do not retain handles."""
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()


def run_sync(config_path, application_dir):
    """Synchronise changed source INIs once and return a task-friendly exit code."""
    logger = build_logger(application_dir / "logs")
    lock = SingleRunLock(application_dir / "ini_share_sync.lock")
    try:
        logger.info("同步开始：配置=%s", config_path)
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
            candidates = find_candidates(config.source_root)
            logger.info(
                "扫描目录：%s；找到 %d 个符合规则的 INI",
                config.source_root,
                len(candidates),
            )

            for candidate in candidates:
                try:
                    fingerprint = sha256_file(candidate.source_path)
                    key = candidate_key(candidate)
                    previous_entry = state.get(key)
                    if previous_entry and previous_entry["sha256"] == fingerprint:
                        logger.info("未变化，跳过：%s", candidate.source_path)
                        continue

                    published_hash = copy_as_txt(
                        candidate.source_path,
                        target_path(config, candidate),
                    )
                    state[key] = {
                        "sha256": published_hash,
                        "synced_at": datetime.now().replace(microsecond=0).isoformat(),
                    }
                    save_state(state_path, state)
                    logger.info("同步成功：%s", candidate.source_path)
                except (OSError, ValueError) as exc:
                    failures += 1
                    logger.error("同步失败：%s；%s", candidate.source_path, exc)

            return 2 if failures else 0
        except (ConfigError, OSError, ValueError) as exc:
            logger.error("本轮未执行：%s", exc)
            return 1
        finally:
            lock.release()
    finally:
        close_logger(logger)


def runtime_directory():
    """Return the directory that holds configuration and run-time state."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def main(argv=None):
    """Parse the optional configuration path and execute one sync pass."""
    parser = argparse.ArgumentParser(description="同步同名 INI 到局域网共享目录")
    parser.add_argument("--config", type=Path, help="配置文件路径")
    arguments = parser.parse_args(argv)
    application_dir = runtime_directory()
    config_path = arguments.config or application_dir / "sync_config.json"
    return run_sync(config_path, application_dir)


if __name__ == "__main__":
    raise SystemExit(main())
