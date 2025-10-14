from ..api_core import status_router as router
from app.data.providers import get_provider


@router.get("/status")
async def status():
    prov = get_provider()
    data = prov.get_status()
    # Add debug flag if available via CONFIG
    try:
        from app.server.CONFIG import DEBUG as _DBG  # type: ignore
        data["debug"] = bool(_DBG)
    except Exception:
        pass
    return data


@router.get("/")
def read_root():
    return {"/docs": "??? /docs ????"}


@router.get("/delay")
async def get_delay():
    return 0


@router.get("/health")
async def health():
    return {"status": "ok"}
