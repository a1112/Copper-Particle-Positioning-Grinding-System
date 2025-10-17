from ..api_core import status_router as router
from app.domain.status import get_status_service


@router.get("/status")
async def status():
    service = get_status_service()
    data = service.fetch_status()
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
