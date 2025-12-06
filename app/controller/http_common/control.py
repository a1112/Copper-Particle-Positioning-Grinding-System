from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from app.common.task_actions import ACTION_META, normalise_action as normalise_task_action
from .program import DEFAULT_ALG_RESULT_PATH
from .state import ControllerState
from .tasks import TaskQueueWriter

LOG = logging.getLogger("controller.http.control")


def _resolve_identifiers(payload: Dict[str, object]) -> Tuple[Optional[int], Optional[int]]:
    def _coerce_int(value: Any) -> Optional[int]:
        try:
            if value is None or value == "":
                return None
            return int(value)
        except (TypeError, ValueError):
            return None

    if not isinstance(payload, dict):
        return None, None

    record_candidates = (
        payload.get("record_id"),
        payload.get("recordId"),
        payload.get("record"),
    )
    workpiece_candidates = (
        payload.get("workpiece_id"),
        payload.get("workpieceId"),
        payload.get("workpiece"),
    )
    record_value = next((candidate for candidate in record_candidates if _coerce_int(candidate) is not None), None)
    workpiece_value = next((candidate for candidate in workpiece_candidates if _coerce_int(candidate) is not None), None)
    return _coerce_int(record_value), _coerce_int(workpiece_value)


def _should_refresh_program(action_key: str) -> bool:
    return "capture" in action_key


def create_control_handler(
    state: ControllerState,
    task_writer: Optional[TaskQueueWriter],
    *,
    device_id: str,
) -> Any:
    def _enqueue(action: str, params: Optional[Dict[str, Any]] = None, *, workpiece_id: Optional[int] = None, record_id: Optional[int] = None) -> None:
        if task_writer is None:
            return
        payload = {}
        if params:
            try:
                payload = dict(params)
            except Exception:
                payload = {}
        try:
            task_writer.enqueue_control_action(
                action=action,
                device_id=device_id,
                params=payload,
                workpiece_id=workpiece_id,
                record_id=record_id,
            )
        except Exception as exc:
            LOG.error("Failed to enqueue hardware task %s: %s", action, exc)

    def handler(action: str, params: Dict[str, object]) -> Dict[str, object]:
        LOG.info("Control handler received action=%s params=%s", action, dict(params))
        normalized = normalise_task_action(action)
        if not normalized:
            state.register_command(action, False, "Empty action")
            return {"ok": False, "message": "Empty action"}

        record_id, workpiece_id = _resolve_identifiers(params or {})

        if normalized == "capture":
            state.register_command(action, True, "Capture command dispatched")
            _enqueue(action, params, workpiece_id=workpiece_id, record_id=record_id)
            _refresh_program_if_needed(state, normalized)
            return {"ok": True, "message": "Capture command dispatched"}

        manual_action_messages: Dict[str, str] = {
            "manual.single_frame_capture": "Manual single-frame capture dispatched",
            "manual.preprocess_roi_cluster": "Manual preprocessing dispatched",
            "manual.defect_detection": "Manual defect detection dispatched",
            "manual.defect_detection_secondary": "Manual defect detection (secondary) dispatched",
            "manual.c5_upload": "Manual C5 upload dispatched",
            "manual.run_command": "Manual run command dispatched",
            "manual.clear_upload": "Manual clear uploaded command dispatched",
            "manual.initialize": "Manual initialization dispatched",
            "manual.initialize_secondary": "Manual initialization (secondary) dispatched",
        }
        if normalized in manual_action_messages:
            message = manual_action_messages[normalized]
            state.register_command(action, True, message)
            _enqueue(action, params, workpiece_id=workpiece_id, record_id=record_id)
            _refresh_program_if_needed(state, normalized)
            return {"ok": True, "message": message}

        if normalized == "reset":
            state.spindle_rpm = 1100.0
            state.torque_bias = 0.2
            state.stop_program()
            state.register_command(action, True, "Reset acknowledged")
            _enqueue(action, params, workpiece_id=workpiece_id, record_id=record_id)
            return {"ok": True, "message": "Reset acknowledged"}

        if normalized == "boost":
            state.spindle_rpm += 50.0
            state.torque_bias = min(state.torque_bias + 0.05, 0.6)
            state.register_command(action, True, "Boost applied")
            _enqueue(action, params, workpiece_id=workpiece_id, record_id=record_id)
            return {"ok": True, "message": "Boost applied"}

        if normalized in {"run.start", "start"}:
            if state.start_program():
                state.register_command(action, True, "Program playback started")
                _enqueue(action, params, workpiece_id=workpiece_id, record_id=record_id)
                return {"ok": True, "message": "Program playback started"}
            state.register_command(action, False, "No program loaded")
            return {"ok": False, "message": "Program not available"}

        if normalized in {"run.stop", "stop"}:
            state.stop_program()
            state.register_command(action, True, "Program playback stopped")
            _enqueue(action, params, workpiece_id=workpiece_id, record_id=record_id)
            return {"ok": True, "message": "Program playback stopped"}

        if normalized in ACTION_META:
            message = f"Control command dispatched: {action}"
            state.register_command(action, True, message)
            _enqueue(action, params, workpiece_id=workpiece_id, record_id=record_id)
            _refresh_program_if_needed(state, normalized)
            return {"ok": True, "message": message}

        state.register_command(action, False, f"Unsupported action: {action}")
        fallback_params = dict(params or {})
        fallback_params["normalized_action"] = normalized
        _enqueue(action, fallback_params, workpiece_id=workpiece_id, record_id=record_id)
        return {"ok": False, "message": f"Unsupported action: {action}"}

    def _refresh_program_if_needed(state_obj: ControllerState, action_key: str) -> None:
        if not _should_refresh_program(action_key):
            return
        refreshed = state_obj.refresh_program_from_alg(DEFAULT_ALG_RESULT_PATH)
        if refreshed:
            LOG.info("Program lines refreshed after action=%s", action_key)
        else:
            LOG.warning("Program refresh skipped for action=%s", action_key)

    return handler


__all__ = ["create_control_handler"]
