from ..api_core import status_router as router
from app.server.data import get_backend


@router.get("/status")
async def status():
    backend = get_backend()
    status_model = await backend.fetch_status()
    payload = status_model.to_dict()
    try:
        from app.server.CONFIG import DEBUG as _DBG  # type: ignore
        payload["debug"] = bool(_DBG)
    except Exception:
        pass
    return payload


@router.get("/")
def read_root():
    return {"/docs": "??? /docs ????"}


@router.get("/delay")
async def get_delay():
    return 0


@router.get("/health")
async def health():
    return {"status": "ok"}
