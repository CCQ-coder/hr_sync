"""PyInstaller entry point for the raw TCP receiver."""

from device_raw_receiver.main import run


if __name__ == "__main__":
    raise SystemExit(run())
