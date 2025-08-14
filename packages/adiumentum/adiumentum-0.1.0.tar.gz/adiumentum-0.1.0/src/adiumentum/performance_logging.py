import json
import os
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path("codeqa/performance/perf_log/perf_log.jsonl")


def get_callback_name(cb: Callable) -> str:
    return getattr(cb, "__name__", None) or cb.__class__.__name__


def log_perf(
    callable_or_none: Callable | None = None,
    *,
    log_path: Path | Callable = DEFAULT_PATH,
    extra_info: dict[str, Any] | None = None,
) -> Callable:
    def wrapper(_callback: Callable) -> Callable:
        if not os.environ.get("LOG_PERFORMANCE"):
            return _callback

        def inner(*args, **kwargs):
            start_time = time.time()
            result = _callback(*args, **kwargs)
            end_time = time.time()

            log_info = (
                {
                    "name": get_callback_name(_callback),
                    "timeElapsed": round(end_time - start_time, 4),
                    "timestamp": datetime.now().isoformat(sep="_")[:-3],
                    "file": _callback.__module__,
                }
                | (extra_info or {})
                | {"args": str(args), "kwargs": str(kwargs)}
            )
            with log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(log_info) + "\n")

            return result

        return inner

    if callable(callable_or_none):
        return wrapper(callable_or_none)
    return wrapper
