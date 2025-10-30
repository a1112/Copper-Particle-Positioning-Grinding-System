from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .program import DEFAULT_ALG_RESULT_PATH, load_program_lines_from_alg

LOG = logging.getLogger("controller.http.state")


def _default_program_lines() -> List[str]:
    try:
        return load_program_lines_from_alg(DEFAULT_ALG_RESULT_PATH)
    except FileNotFoundError:
        LOG.info("Algorithm result file %s not found; using demo program.", DEFAULT_ALG_RESULT_PATH)
    except Exception as exc:
        LOG.warning("Failed to load algorithm program lines: %s", exc)
    return [
        "%",
        "O3000 (HTTP DEMO)",
        "G90 G21 G17",
        "G0 X0.000 Y0.000 Z5.000",
        "G1 X20.000 Y0.000 Z-0.200 F800.0",
        "G1 X20.000 Y20.000 Z-0.200",
        "G1 X0.000 Y20.000 Z-0.200",
        "G1 X0.000 Y0.000 Z-0.200",
        "G0 Z5.000",
        "M30",
    ]


@dataclass
class ControllerState:
    """Mutable controller state shared by simulator and production runners."""

    label: str = "http-controller"
    run_mode: str = "HTTP"
    spindle_rpm: float = 1200.0
    torque_bias: float = 0.3
    command_log: List[Dict[str, str]] = field(default_factory=list)
    program_lines: List[str] = field(default_factory=_default_program_lines)
    program_current: int = -1
    program_running: bool = False
    _program_dirty: bool = True

    def register_command(self, action: str, ok: bool, message: str) -> None:
        self.command_log.append(
            {
                "ts": time.time(),
                "level": "INFO" if ok else "WARN",
                "name": "controller",
                "msg": f"control action={action} message={message}",
            }
        )

    def refresh_program_from_alg(self, path: Optional[Path] = None) -> bool:
        program_path = Path(path) if path is not None else DEFAULT_ALG_RESULT_PATH
        try:
            lines = load_program_lines_from_alg(program_path)
        except FileNotFoundError:
            LOG.warning("Program refresh skipped; algorithm result file %s is missing.", program_path)
            return False
        except Exception as exc:
            LOG.error("Program refresh failed for %s: %s", program_path, exc)
            return False
        self.program_lines = list(lines)
        self.mark_program_dirty()
        LOG.info("Program lines refreshed from %s (%d entries).", program_path, len(self.program_lines))
        return True

    def start_program(self) -> bool:
        if not self.program_lines:
            return False
        self.program_running = True
        self.program_current = -1
        self._program_dirty = True
        return True

    def stop_program(self) -> None:
        self.program_running = False
        self.program_current = -1
        self._program_dirty = True

    def advance_program(self) -> None:
        if not self.program_running or not self.program_lines:
            return
        self.program_current = (self.program_current + 1) % len(self.program_lines)
        self._program_dirty = True

    def mark_program_dirty(self) -> None:
        self._program_dirty = True

    def program_snapshot(self) -> Optional[Dict[str, object]]:
        if not self._program_dirty:
            return None
        self._program_dirty = False
        state_label = "RUNNING" if self.program_running else "IDLE"
        return {
            "program": list(self.program_lines),
            "program_state": {"state": state_label, "current": self.program_current},
        }


__all__ = ["ControllerState"]
