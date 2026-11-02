"""Package entry point for IniShareSync."""

if __name__ == "__main__":
    try:
        from ini_share_sync.main import main

        raise SystemExit(main())
    except Exception:
        # A windowless scheduled task must exit instead of showing a traceback dialog.
        raise SystemExit(1)
