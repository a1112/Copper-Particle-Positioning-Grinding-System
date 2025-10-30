from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

LOG = logging.getLogger("controller.http.program")

DEFAULT_ALG_RESULT_PATH = Path("D:/SaveData/alg_result.json")


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _format_float(value: Any, precision: int = 1) -> str:
    return f"{_safe_float(value):.{precision}f}"


def _format_avoid_tag(*candidates: str) -> str:
    joined = ",".join(filter(None, (candidate or "" for candidate in candidates)))
    return joined or "-"


def _format_point_line(
    index: int,
    image_point: Mapping[str, Any],
    robot_point: Mapping[str, Any],
    precision: int,
) -> str:
    def fmt(source: Mapping[str, Any], key: str) -> str:
        return _format_float(source.get(key), precision)

    avoid = _format_avoid_tag(
        str(image_point.get("strQgNotSafe", "")).strip(),
        str(robot_point.get("strQgNotSafe", "")).strip(),
    )
    image_descriptor = (
        f"x={fmt(image_point, 'fX')},y={fmt(image_point, 'fY')},z={fmt(image_point, 'fZ')},"
        f"row={fmt(image_point, 'fRow')},col={fmt(image_point, 'fCol')}"
    )
    robot_descriptor = (
        f"x={fmt(robot_point, 'fX')},y={fmt(robot_point, 'fY')},z={fmt(robot_point, 'fZ')}"
    )
    meta_descriptor = (
        f"def={image_point.get('iDef', robot_point.get('iDef', '-'))},"
        f"depth={fmt(image_point, 'MxHeightCur')},"
        f"zmax={fmt(image_point, 'ZMaxRelDm')},"
        f"avoid={avoid}"
    )
    return f"({index}) image[{image_descriptor}] robot[{robot_descriptor}] {meta_descriptor}"


def load_program_lines_from_alg(path: Path = DEFAULT_ALG_RESULT_PATH, *, precision: int = 1) -> List[str]:
    """Load the path planning result produced by the algorithm into controller program lines."""
    raw = path.read_text(encoding="utf-8")
    data: Dict[str, Any] = json.loads(raw)

    image_points: Sequence[Mapping[str, Any]] = data.get("sListPPtsImage") or []
    robot_points: Sequence[Mapping[str, Any]] = data.get("sListPPtsRobot") or []

    if len(image_points) != len(robot_points):
        raise ValueError("Image and robot point lists must be the same length.")

    precision = max(0, precision)

    lines: List[str] = []
    summary = (
        f"summary: result={'PASS' if data.get('bTJG') else 'FAIL'} "
        f"points={len(image_points)} time={_format_float(data.get('time', 0.0), precision)}s "
        f"region={'yes' if data.get('hasRegionMxAllList') else 'no'}"
    )
    lines.append(summary)

    for idx, (image_point, robot_point) in enumerate(zip(image_points, robot_points), start=1):
        try:
            lines.append(_format_point_line(idx, image_point, robot_point, precision))
        except Exception as exc:  # pragma: no cover - defensive
            LOG.warning("Failed to format point index=%d: %s", idx, exc)
            continue

    return lines


__all__ = ["DEFAULT_ALG_RESULT_PATH", "load_program_lines_from_alg"]
