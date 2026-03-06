from __future__ import annotations

import json
from pathlib import Path


REQUIRED_KEYS = {"date", "source", "title"}


def load_news_items(path: str) -> list[dict]:
    raw = Path(path).read_text(encoding="utf-8")
    data = json.loads(raw)

    if not isinstance(data, list):
        raise ValueError("News file must be a JSON array")

    cleaned: list[dict] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"News item at index {idx} is not an object")

        missing = REQUIRED_KEYS - set(item.keys())
        if missing:
            raise ValueError(f"News item at index {idx} missing keys: {sorted(missing)}")

        cleaned.append(
            {
                "date": str(item["date"]),
                "source": str(item["source"]),
                "title": str(item["title"]),
            }
        )

    return cleaned
