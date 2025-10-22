"""Utilities for parsing machine/tool metadata from exported documents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


class MetaDataLoader:
    """Load and extract metadata fields used by various API endpoints."""

    def __init__(self, file_path: str | Path | None = None) -> None:
        base_dir = Path(__file__).resolve().parents[4]
        default_file = base_dir / "docs" / "MzPoliShine.km"
        self._file_path = Path(file_path) if file_path else default_file

    # Public API -------------------------------------------------------------

    def extract(self) -> Dict[str, Any]:
        """
        Return a dictionary with pre-defined metadata fields.

        The structure mirrors the payload historically returned by
        ``GET /config/meta`` so existing consumers keep working.
        """
        texts = self._load_texts()
        if not texts:
            return {
                "nodes": 0,
                "cutter_diameter": "",
                "tool_life": "",
                "control_mode": "",
                "stage_mode": "",
                "plane_height": "",
                "board_serial": "",
                "particle_count": "",
            }

        def find_first(markers: Sequence[str]) -> str:
            for text in texts:
                if any(marker in text for marker in markers):
                    return text
            return ""

        return {
            "nodes": len(texts),
            "cutter_diameter": find_first(["??", "????"]),
            "tool_life": find_first(["??", "????"]),
            "control_mode": find_first(["????"]),
            "stage_mode": find_first(["???", "????"]),
            "plane_height": find_first(["????", "????"]),
            "board_serial": find_first(["???", "??"]),
            "particle_count": find_first(["????", "????"]),
        }

    # Internal helpers -------------------------------------------------------

    def _load_texts(self) -> List[str]:
        if not self._file_path.exists():
            return []
        raw = self._file_path.read_bytes()
        data: Dict[str, Any]
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            try:
                data = json.loads(raw.decode("gbk", errors="ignore"))
            except Exception:
                return []

        texts: List[str] = []

        def walk(node: Dict[str, Any]) -> None:
            payload = node.get("data") or {}
            text = payload.get("text")
            if isinstance(text, str):
                texts.append(text)
            for child in node.get("children") or []:
                if isinstance(child, dict):
                    walk(child)

        root = data.get("root")
        if isinstance(root, dict):
            walk(root)
        return texts


__all__ = ["MetaDataLoader"]
