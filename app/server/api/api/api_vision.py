from __future__ import annotations

from fastapi import HTTPException

from app.server.api.services.calibration_loader import CalibrationSettingsLoader
from ..api_core import vision_router as router

_CALIBRATION_LOADER = CalibrationSettingsLoader()


@router.get("/vision/calibration")
async def get_calibration() -> dict:
    data = _CALIBRATION_LOADER.load()
    if not data:
        raise HTTPException(status_code=404, detail="Calibration data not available")
    return data
