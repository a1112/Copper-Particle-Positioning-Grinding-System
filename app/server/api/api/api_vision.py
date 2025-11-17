from __future__ import annotations

from fastapi import HTTPException

from app.server.api.services.calibration_manager import CalibrationManager
from app.server.api.services.task1_runtime import get_task1_runner
from ..api_core import vision_router as router

_CALIBRATION_MANAGER = CalibrationManager()


@router.get("/vision/calibration")
async def get_calibration() -> dict:
    data = _CALIBRATION_MANAGER.ensure_active_payload()
    if not data:
        raise HTTPException(status_code=404, detail="Calibration data not available")
    return data


@router.get("/vision/cameras")
def list_cameras() -> dict:
    runner = get_task1_runner()
    return {"profiles": runner.camera_profiles()}


@router.get("/vision/calibrations")
async def list_calibrations() -> dict:
    return _CALIBRATION_MANAGER.list_overview()


@router.post("/vision/calibrations")
async def create_calibration(payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return _CALIBRATION_MANAGER.create_group(
            name=payload.get("name"),
            record_id=payload.get("record_id"),
        )
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/vision/calibrations/{name}")
async def get_calibration_group(name: str) -> dict:
    try:
        return _CALIBRATION_MANAGER.load_group(name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/vision/calibrations/{name}/activate")
async def activate_calibration_group(name: str) -> dict:
    try:
        return _CALIBRATION_MANAGER.set_active(name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/vision/calibrations/{name}/data")
async def save_calibration_group(name: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return _CALIBRATION_MANAGER.save_group_data(name, payload)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/vision/calibrations/{name}")
async def delete_calibration_group(name: str) -> dict:
    try:
        return _CALIBRATION_MANAGER.delete_group(name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/vision/calibrations/{name}/import-image")
async def import_calibration_image(name: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    source_path = payload.get("source_path")
    use_current = bool(payload.get("use_current"))
    try:
        return _CALIBRATION_MANAGER.import_image(name, source_path=source_path, use_current=use_current)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/vision/calibrations/{name}/rename")
async def rename_calibration_group(name: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    new_name = (payload.get("name") or "").strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="New calibration name must not be empty")
    try:
        return _CALIBRATION_MANAGER.rename_group(name, new_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/vision/calibrations/{name}/compute")
async def compute_calibration_matrices(name: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    points = payload.get("points") or []
    if not isinstance(points, list):
        raise HTTPException(status_code=400, detail="points must be a list")
    matrices = _CALIBRATION_MANAGER.compute_matrices(points)
    return {"matrices": matrices}
