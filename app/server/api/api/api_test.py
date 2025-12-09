from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from app import config
from app.db import SessionLocal
from app.server.api.services.task1_runtime import get_task1_runner
from app.server.api.services.settings_store import SettingsStore
from app.vision.task1.service import Task1RunError, Task1RunOptions

from ..api_core import test_router as router

_SETTINGS_STORE = SettingsStore()


class Task1RunPayload(BaseModel):
    mode: Literal["capture", "folder"] = "capture"
    folder: Optional[str] = None
    camera_profile: Optional[str] = Field(None, alias="cameraProfile")
    camera_serial: Optional[str] = Field(None, alias="cameraSerial")
    overrides: Dict[str, Any] = Field(default_factory=dict)
    build_visuals: bool = Field(True, alias="buildVisuals")

    class Config:
        validate_by_name = True


def _format_capture(data) -> Optional[Dict[str, Any]]:
    if data is None:
        return None
    return {
        "profile": data.profile,
        "source_dir": str(data.source_dir),
        "message": data.message,
        "files": [str(path) for path in data.files],
    }


@router.get("/test/task1/defaults")
def get_task1_defaults() -> Dict[str, Any]:
    runner = get_task1_runner()
    camera_defaults = _load_camera_settings()
    return {
        "parameters": runner.parameter_schema(),
        "camera_profiles": runner.camera_profiles(),
        "save_dir": str(config.SAVE_DATA_CURRENT_DIR),
        "default_camera": camera_defaults.profile,
        "default_serial": camera_defaults.serial,
    }


@router.post("/test/task1/run")
async def run_task1(payload: Task1RunPayload) -> Dict[str, Any]:
    runner = get_task1_runner()
    camera_defaults = _load_camera_settings()
    profile = payload.camera_profile or camera_defaults.profile
    serial = payload.camera_serial or camera_defaults.serial
    options = Task1RunOptions(
        mode=payload.mode,
        folder=payload.folder,
        camera_profile=profile,
        camera_serial=serial,
        overrides=payload.overrides,
        build_visuals=payload.build_visuals,
    )
    try:
        result = await run_in_threadpool(runner.run, options)
    except Task1RunError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "metrics": result.metrics,
        "summary_path": str(result.summary_path),
        "output_dir": str(result.output_dir),
        "source_dir": str(result.source_dir),
        "capture": _format_capture(result.capture),
        "visuals": {key: [str(path) for path in paths] for key, paths in result.visuals.items()},
    }


class _CameraDefaults:
    def __init__(self, profile: Optional[str], serial: Optional[str]) -> None:
        self.profile = profile
        self.serial = serial


def _load_camera_settings() -> _CameraDefaults:
    session = SessionLocal()
    try:
        general = _SETTINGS_STORE.fetch_category(session, "general")
    finally:
        session.close()
    camera = general.get("camera")
    profile: Optional[str] = None
    serial: Optional[str] = None
    if isinstance(camera, dict):
        if isinstance(camera.get("profile"), str) and camera.get("profile"):
            profile = camera.get("profile")
        if isinstance(camera.get("serial"), str) and camera.get("serial"):
            serial = camera.get("serial")
    if not profile:
        profile = "sim"
    return _CameraDefaults(profile=profile, serial=serial)
