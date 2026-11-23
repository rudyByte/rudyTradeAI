from __future__ import annotations

import argparse

from .config import Settings
from .db import initialize
from .logging_config import configure_logging


def main() -> None:
    parser = argparse.ArgumentParser(prog="rudytrade")
    parser.add_argument("command", choices=["init-db"])
    args = parser.parse_args()
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    if args.command == "init-db":
        initialize(settings.db_path)
        print(f"Initialized paper-only database at {settings.db_path}")


if __name__ == "__main__":
    main()
