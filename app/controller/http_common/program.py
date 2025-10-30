from __future__ import annotations

import json
import logging
from pathlib import Path
from math import sqrt
from typing import Any, Dict, List, Mapping, Sequence

LOG = logging.getLogger("controller.http.program")

DEFAULT_ALG_RESULT_PATH = Path("D:/SaveData/alg_result.json")


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _format_float(value: Any, precision: int = 1) -> str:
    return f"{_safe_float(value):.{precision}f}"


def _vector_distance(prev_point: Mapping[str, Any], next_point: Mapping[str, Any]) -> float:
    dx = _safe_float(next_point.get("fX")) - _safe_float(prev_point.get("fX"))
    dy = _safe_float(next_point.get("fY")) - _safe_float(prev_point.get("fY"))
    dz = _safe_float(next_point.get("fZ")) - _safe_float(prev_point.get("fZ"))
    return sqrt(dx * dx + dy * dy + dz * dz)


def _format_command_line(
    target_index: int,
    previous_robot_point: Mapping[str, Any],
    target_robot_point: Mapping[str, Any],
    target_image_point: Mapping[str, Any],
    precision: int,
) -> str:
    command = "FastMov" if target_index <= 4 else "FastCut"

    x = _format_float(target_robot_point.get("fX"), precision)
    y = _format_float(target_robot_point.get("fY"), precision)
    z = _format_float(target_robot_point.get("fZ"), precision)

    speed = _format_float(_vector_distance(previous_robot_point, target_robot_point), precision)
    rpm_source = target_image_point.get("ZMaxRelDm", 0.0) if command == "FastCut" else 0.0
    rpm = _format_float(rpm_source, precision)

    return f"{command} X:{x} Y:{y} Z:{z} V:{speed} R:{rpm}"


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

    if len(robot_points) < 2:
        LOG.warning("Algorithm produced fewer than two points; no motion commands generated.")
        return lines

    for idx in range(1, len(robot_points)):
        try:
            command_line = _format_command_line(
                idx + 1,
                robot_points[idx - 1],
                robot_points[idx],
                image_points[idx],
                precision,
            )
        except Exception as exc:  # pragma: no cover - defensive
            LOG.warning("Failed to format command for segment ending at index=%d: %s", idx + 1, exc)
            continue
        lines.append(command_line)

    return lines


__all__ = ["DEFAULT_ALG_RESULT_PATH", "load_program_lines_from_alg"]
