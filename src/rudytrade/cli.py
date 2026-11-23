from __future__ import annotations

import argparse

from .cloud import check_all
from .config import Settings, load_env_file
from .db import initialize
from .logging_config import configure_logging


def main() -> None:
    parser = argparse.ArgumentParser(prog="rudytrade")
    parser.add_argument("command", choices=["init-db", "check-cloud"])
    args = parser.parse_args()
    load_env_file()
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    if args.command == "init-db":
        initialize(settings.db_path)
        print(f"Initialized paper-only database at {settings.db_path}")
    elif args.command == "check-cloud":
        failed = False
        for status in check_all():
            print(f"{'ok' if status.ok else 'failed'}  {status.service}: {status.detail}")
            failed = failed or not status.ok
        raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
