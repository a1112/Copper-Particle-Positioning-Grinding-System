from __future__ import annotations

from typing import Any, Dict, List
from starlette.responses import JSONResponse
from ..api_core import path_router as router
from ..ws.code_bus import bus


from app.process.path_planning import (
    generate_test_heightmap,
    plan_toolpath,
    summarize_path,
    CutParams,
)
from app.process.gcode_export import to_gcode


@router.get('/path/elevation')
async def path_elevation(mode: str = 'sim'):
    try:
        # For now, provide a simulated path: s in [0..100], z a smooth varying depth
        n = 200
        pts: List[Dict[str, float]] = []
        import math
        for i in range(n + 1):
            s = float(i) * (100.0 / n)
            z = -abs(math.sin(i / 12.0)) * 0.8  # below baseline
            pts.append({'s': s, 'z': round(z, 4)})
        cuts = [
            {'s': 10.0, 'z': -0.2, 'amount': 0.2},
            {'s': 30.0, 'z': -0.5, 'amount': 0.5},
            {'s': 60.0, 'z': -0.3, 'amount': 0.3},
            {'s': 85.0, 'z': -0.7, 'amount': 0.7},
        ]
        return {'base': 0.0, 'points': pts, 'cuts': cuts}
    except Exception as e:
        return JSONResponse(status_code=500, content={'ok': False, 'error': str(e)})


@router.post('/path/plan')
async def plan_path(
    mode: str = 'discrete',  # 'discrete' or 'concentrated'
    width: int = 200,
    height: int = 200,
    pixel_mm: float = 0.2,
    blobs: int = 25,
    clustered_ratio: float = 0.4,
) -> Any:
    """
    Generate a simulated heightmap and plan a lateral-only toolpath.
    Publishes the generated G-code to the Code WebSocket and returns a summary.
    """
    try:
        hm, px = generate_test_heightmap(size=(height, width), pixel_mm=pixel_mm, n_blobs=blobs, clustered_ratio=clustered_ratio)
        params = CutParams()
        path = plan_toolpath(hm, px, mode=mode, params=params)
        gcode = to_gcode(path, params=params)
        # Publish program to /ws/code subscribers
        await bus.set_program(gcode)
        # Also mark state as IDLE with current = -1 after publish
        await bus.set_state("IDLE", -1)
        return {
            'ok': True,
            'mode': mode,
            'pixel_mm': px,
            'summary': summarize_path(path),
            'program_lines': len(gcode),
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={'ok': False, 'error': str(e)})
