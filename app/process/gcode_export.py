from __future__ import annotations

from typing import Iterable, List

from .path_planning import ToolPath, Segment, CutParams


def to_gcode(path: ToolPath, params: CutParams | None = None) -> List[str]:
    """Translate ToolPath into a simple absolute G-code program (mm)."""
    params = params or CutParams()
    lines: List[str] = []
    emit = lines.append
    emit("%")
    emit("O1002 (Auto Plan)")
    emit("G90 G21 G17")  # abs, mm, XY plane
    emit(f"G0 Z{params.z_safe:.3f}")
    emit("M3 S12000")
    feed = params.feed_mm_min
    for seg in path.segments:
        if not seg.pts:
            continue
        if seg.kind == "rapid":
            x, y, z = seg.pts[0]
            emit(f"G0 X{x:.3f} Y{y:.3f} Z{z:.3f}")
        elif seg.kind == "ramp":
            # Linear ramp-in with feed
            p0 = seg.pts[0]
            for (x, y, z) in seg.pts[1:]:
                emit(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F{feed:.1f}")
        elif seg.kind == "cut":
            # Lateral cutting at constant Z
            for (x, y, z) in seg.pts:
                emit(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F{feed:.1f}")
        else:
            # Unknown: treat as rapid to last point
            x, y, z = seg.pts[-1]
            emit(f"G0 X{x:.3f} Y{y:.3f} Z{z:.3f}")
    emit(f"G0 Z{params.z_safe:.3f}")
    emit("M5")
    emit("M30")
    return lines

