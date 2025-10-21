from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

import numpy as np

from .path_planning import (
    CutParams,
    ToolPath,
    generate_test_heightmap,
    plan_toolpath,
    summarize_path,
)


@dataclass
class SimulatedPlan:
    """Container with the computed toolpath, summary metrics and metadata."""

    path: ToolPath
    summary: Dict[str, Any]
    heightmap: np.ndarray
    pixel_mm: float


class SimulatedPathPlanner:
    """Facade around the pure functions in ``path_planning`` for simulator use."""

    def __init__(self, params: CutParams | None = None) -> None:
        self.params = params or CutParams()

    def generate_heightmap(
        self,
        size: Tuple[int, int] = (200, 200),
        pixel_mm: float = 0.2,
        seed: int | None = 42,
        n_blobs: int = 25,
        clustered_ratio: float = 0.4,
    ) -> Tuple[np.ndarray, float]:
        return generate_test_heightmap(
            size=size,
            pixel_mm=pixel_mm,
            seed=seed,
            n_blobs=n_blobs,
            clustered_ratio=clustered_ratio,
        )

    def plan_from_heightmap(
        self,
        height_mm: np.ndarray,
        pixel_mm: float,
        mode: str = "discrete",
    ) -> ToolPath:
        return plan_toolpath(height_mm, pixel_mm, mode=mode, params=self.params)

    def summarize(self, tool_path: ToolPath) -> Dict[str, Any]:
        return summarize_path(tool_path)

    def demo_plan(
        self,
        *,
        size: Tuple[int, int] = (200, 200),
        pixel_mm: float = 0.2,
        seed: int | None = 42,
        mode: str = "discrete",
    ) -> SimulatedPlan:
        height, px_mm = self.generate_heightmap(size=size, pixel_mm=pixel_mm, seed=seed)
        tool_path = self.plan_from_heightmap(height, px_mm, mode=mode)
        summary = self.summarize(tool_path)
        return SimulatedPlan(path=tool_path, summary=summary, heightmap=height, pixel_mm=px_mm)
