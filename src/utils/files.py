from __future__ import annotations

from pathlib import Path


def read_text(path: str | Path) -> str:
    with open(Path(path), "r", encoding="utf-8", newline="") as file:
        return file.read()


def write_text(path: str | Path, text: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as file:
        file.write(text)