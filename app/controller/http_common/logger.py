from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterable


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)


class HttpBridgeFileLogger:
    """Append structured controller telemetry to date-partitioned log files."""

    def __init__(self, root: Path, *, encoding: str = "utf-8") -> None:
        self._root = Path(root)
        self._encoding = encoding
        self._root.mkdir(parents=True, exist_ok=True)

    def write(self, category: str, payload: Any, **extra: Any) -> None:
        entry: Dict[str, Any] = {
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "payload": payload,
        }
        if extra:
            entry.update(extra)
        self._append(category, entry)

    def write_many(self, category: str, payloads: Iterable[Any], **extra: Any) -> None:
        for item in payloads:
            self.write(category, item, **extra)

    def _append(self, category: str, entry: Dict[str, Any]) -> None:
        safe_category = category or "logs"
        category_dir = self._root / safe_category
        category_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.now():%Y-%m-%d}.log"
        path = category_dir / filename
        with path.open("a", encoding=self._encoding) as fh:
            json.dump(entry, fh, ensure_ascii=False, default=_json_default)
            fh.write("\n")


__all__ = ["HttpBridgeFileLogger"]
