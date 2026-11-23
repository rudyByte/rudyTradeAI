from __future__ import annotations

import os
import time


def process_status() -> dict[str, object]:
    return {"status": "HEALTHY", "pid": os.getpid(), "uptime_supported": False, "checked_at_epoch": time.time()}
