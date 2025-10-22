from __future__ import annotations

from ..api_core import tool_router as router
from app.server.data import get_backend


@router.get("/toolInfo")
async def tool_info():
    backend = get_backend()
    snapshot = await backend.fetch_tool_info()
    return snapshot.to_dict()
