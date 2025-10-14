from __future__ import annotations

from typing import Any, Dict, List
from starlette.responses import JSONResponse
from ..api_core import path_router as router


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
