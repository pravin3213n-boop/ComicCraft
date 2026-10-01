from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID
from typing import Any

from app.config import COMICS_DIR


def _record_path(comic_id: str) -> Path | None:
    try:
        safe_id = str(UUID(comic_id))
    except (ValueError, TypeError, AttributeError):
        return None
    return COMICS_DIR / f"{safe_id}.json"


def save_comic(record: dict[str, Any]) -> None:
    path = _record_path(str(record.get("id", "")))
    if path is None:
        raise ValueError("Invalid comic ID.")
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def load_comic(comic_id: str) -> dict[str, Any] | None:
    path = _record_path(comic_id)
    if path is None or not path.is_file():
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return record if isinstance(record, dict) and record.get("id") == str(UUID(comic_id)) else None
