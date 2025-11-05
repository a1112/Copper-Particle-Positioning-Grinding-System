from __future__ import annotations

import json
import logging
from pathlib import Path
from math import sqrt
from typing import Any, Dict, List, Mapping, Optional, Sequence

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


def build_program_lines_from_alg_data(data: Mapping[str, Any], *, precision: int = 1) -> List[str]:
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


def load_program_lines_from_alg(path: Path = DEFAULT_ALG_RESULT_PATH, *, precision: int = 1) -> List[str]:
    raw = path.read_text(encoding="utf-8")
    data: Dict[str, Any] = json.loads(raw)
    return build_program_lines_from_alg_data(data, precision=precision)


def build_commands_from_alg_data(data: Mapping[str, Any]) -> List[Dict[str, float]]:
    robot_points: Sequence[Mapping[str, Any]] = data.get("sListPPtsRobot") or []
    image_points: Sequence[Mapping[str, Any]] = data.get("sListPPtsImage") or []
    if len(robot_points) < 2:
        return []

    commands: List[Dict[str, float]] = []
    for idx in range(1, len(robot_points)):
        prev_robot = robot_points[idx - 1]
        curr_robot = robot_points[idx]
        image_point = image_points[idx] if idx < len(image_points) else {}
        commands.append(
            {
                "ex": _safe_float(curr_robot.get("fX")),
                "ey": _safe_float(curr_robot.get("fY")),
                "ez": _safe_float(curr_robot.get("fZ")),
                "r": _safe_float(
                    image_point.get("ZMaxRelDm", curr_robot.get("ZMaxRelDm", curr_robot.get("MxHeightCur", 0.0)))
                ),
                "v": _vector_distance(prev_robot, curr_robot),
                "def": curr_robot.get("iDef"),
            }
        )
    return commands


def _convert_point_for_preview(point: Mapping[str, Any], *, is_image: bool) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    if is_image:
        result["x"] = _safe_float(point.get("fCol"))
        result["y"] = _safe_float(point.get("fRow"))
    else:
        result["x"] = _safe_float(point.get("fX"))
        result["y"] = _safe_float(point.get("fY"))
        result["z"] = _safe_float(point.get("fZ"))
    if "iDef" in point:
        result["def"] = point.get("iDef")
    if "ZMaxRelDm" in point:
        result["ZMaxRelDm"] = _safe_float(point.get("ZMaxRelDm"))
    if "MxHeightCur" in point:
        result["MxHeightCur"] = _safe_float(point.get("MxHeightCur"))
    cyl = point.get("strQgNotSafe") or point.get("cylinderBypass")
    if cyl:
        result["cylinderBypass"] = cyl
    return result


def build_path_preview_from_alg_data(data: Mapping[str, Any]) -> List[Dict[str, Any]]:
    image_points: Sequence[Mapping[str, Any]] = data.get("sListPPtsImage") or []
    robot_points: Sequence[Mapping[str, Any]] = data.get("sListPPtsRobot") or []
    if not image_points and not robot_points:
        return []

    preview_entry: Dict[str, Any] = {
        "display": f"path ({len(robot_points) or len(image_points)} pts)",
        "type": "path",
        "imagePath": [_convert_point_for_preview(pt, is_image=True) for pt in image_points],
        "robotPath": [_convert_point_for_preview(pt, is_image=False) for pt in robot_points],
    }
    if robot_points:
        preview_entry["start"] = _convert_point_for_preview(robot_points[0], is_image=False)
        preview_entry["end"] = _convert_point_for_preview(robot_points[-1], is_image=False)
    return [preview_entry]


def normalise_camera_matrix(raw: Any) -> Optional[List[List[float]]]:
    if raw is None:
        return None
    if isinstance(raw, dict):
        if "data" in raw:
            raw = raw["data"]
        else:
            raw = list(raw.values())
    if not isinstance(raw, (list, tuple)):
        return None

    values: List[float] = []
    for item in raw:
        try:
            values.append(float(item))
        except (TypeError, ValueError):
            values.append(0.0)

    matrix: List[List[float]] = []
    if len(values) == 16:
        for row in range(4):
            matrix.append(values[row * 4 : (row + 1) * 4])
    elif len(values) == 12:
        for row in range(3):
            row_values = values[row * 4 : (row + 1) * 4]
            while len(row_values) < 4:
                row_values.append(0.0)
            matrix.append(row_values)
    else:
        return None

    while len(matrix) < 4:
        matrix.append([0.0, 0.0, 0.0, 0.0])

    matrix[3][0] = 0.0
    matrix[3][1] = 0.0
    matrix[3][2] = 0.0
    matrix[3][3] = 1.0
    return matrix


def build_program_payload_from_alg_data(data: Mapping[str, Any], *, precision: int = 1) -> Dict[str, Any]:
    try:
        lines = build_program_lines_from_alg_data(data, precision=precision)
    except Exception as exc:  # pragma: no cover - defensive
        LOG.warning("Failed to build program lines from algorithm data: %s", exc)
        lines = []
    commands = build_commands_from_alg_data(data)
    path_preview = build_path_preview_from_alg_data(data)
    camera_matrix = normalise_camera_matrix(
        data.get("camera_to_robot_matrix") or data.get("cameraToRobotHomMat3d") or data.get("CameraToRobotHomMat3d")
    )

    payload: Dict[str, Any] = {
        "lines": lines,
        "commands": commands,
        "path_preview": path_preview,
        "sListPPtsImage": data.get("sListPPtsImage") or [],
        "sListPPtsRobot": data.get("sListPPtsRobot") or [],
        "fixtures": data.get("fixtures") or [],
        "camera_to_robot_matrix": camera_matrix,
        "machine_matrix": camera_matrix,
        "alg_result": data,
    }
    return payload


__all__ = [
    "DEFAULT_ALG_RESULT_PATH",
    "build_program_lines_from_alg_data",
    "build_commands_from_alg_data",
    "build_path_preview_from_alg_data",
    "build_program_payload_from_alg_data",
    "load_program_lines_from_alg",
    "normalise_camera_matrix",
]
