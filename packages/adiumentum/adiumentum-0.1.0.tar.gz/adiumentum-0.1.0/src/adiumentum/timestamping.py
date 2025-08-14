from datetime import datetime
from pathlib import Path


def insert_timestamp(p: Path | str) -> Path:
    new_path = str(p)

    if "." in new_path:
        base, suffix = new_path.rsplit(".", 1)
        return Path(f"{base}__{datetime.now():%Y-%m-%d_%H:%M:%S}.{suffix}")

    return Path(f"{new_path}__{datetime.now():%Y-%m-%d_%H:%M:%S}")
