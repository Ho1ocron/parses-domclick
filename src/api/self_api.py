import logging
import sys
from types import TracebackType

import httpx


def is_selenium_ready(host, port, timeout=60):
    url = f"http://{host}:{port}/status"
    try:
        r: dict[str, dict] = httpx.get(url).json()
        if r.get("value", {}).get("ready"):
            return True
    except Exception:
        pass
    return False


def except_hook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
):
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    logging.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(1)