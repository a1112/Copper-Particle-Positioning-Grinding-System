from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

# Support both `python -m task1.main` and `python task1/main.py` execution
try:  # Prefer package-relative imports when run as a module
    from .config import TaskConfig
    from .export import export_summary, export_visuals
    from .pipeline import run_pipeline
except ImportError:  # Fallback for direct script execution without a package context
    import sys
    from pathlib import Path as _Path

    project_root = _Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    from app.vision.task1.config import TaskConfig
    from app.vision.task1.export import export_summary, export_visuals
    from app.vision.task1.pipeline import run_pipeline


def main(argv: Optional[Iterable[str]] = None) -> None:
    """运行任务 1 完整管线并导出结果。"""
    config = TaskConfig.from_args(argv)
    result, visuals = run_pipeline(config, build_visuals=True)
    output_dir = config.output_dir
    summary_path = export_summary(result, config, output_dir / "task1_result.json")
    export_visuals(output_dir, visuals)

    print("Task 1 pipeline completed successfully.")
    print(f"- Board plane RMS error: {result.plane.rms_error:.3f} mm")
    print(f"- Detected fixtures: {len(result.fixtures)}")
    print(f"- Detected particle clusters: {len(result.particles)}")
    print(f"- Toolpath segments: {len(result.toolpaths.segments)}")
    print(f"- Summary written to: {summary_path}")


if __name__ == "__main__":
    main()
