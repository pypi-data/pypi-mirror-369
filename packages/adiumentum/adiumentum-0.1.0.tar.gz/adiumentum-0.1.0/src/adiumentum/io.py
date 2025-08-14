import json
import os
from pathlib import Path


def list_full(directory: str | Path, ending: str = "") -> list[Path]:
    directory = Path(directory)
    return sorted([directory / file for file in os.listdir(directory) if file.endswith(ending)])


def read_raw(json_path: Path) -> str:
    with open(json_path, encoding="utf-8") as f:
        return f.read()


def read_json(json_path: Path) -> dict | list:
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def write_json(python_obj: dict | list | bytes, json_path: Path) -> None:
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(python_obj, f, indent=4, ensure_ascii=False)


def write_raw(text: str, file_path: Path) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def write_raw_bytes(text: bytes, json_path: Path) -> None:
    with open(json_path, "wb") as f:
        f.write(text)
