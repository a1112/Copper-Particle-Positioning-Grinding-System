from __future__ import annotations

import argparse
import importlib
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence
import MechEye
LOG = logging.getLogger(__name__)

try:  # Optional deps for saving outputs
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - numpy optional for CLI usage only
    np = None  # type: ignore

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover - cv2 optional
    cv2 = None  # type: ignore


@dataclass
class CaptureResult:
    color_path: Optional[Path]
    depth_path: Optional[Path]
    point_cloud_path: Optional[Path]


class MechEyeCapture:
    """Thin wrapper around MechEyeAPI to acquire 2D/3D frames and persist them."""

    def __init__(self, output_dir: Path | str = Path("runs") / "mecheye"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._api = importlib.import_module("MechEye")
        self._device_cls = getattr(self._api, "Device", None)
        if self._device_cls is None:
            raise RuntimeError("MechEyeAPI.Device is unavailable; ensure MechEye SDK is installed.")

        self._frame2d_cls = getattr(self._api, "Frame2D", None)
        self._frame3d_cls = getattr(self._api, "Frame3D", None)
        self._status_cls = getattr(self._api, "CameraStatus", None)
        self._device = self._device_cls()

    # --------------------------------------------------------------------- #
    # Device discovery / connection helpers
    # --------------------------------------------------------------------- #

    def discover(self) -> Sequence[Any]:
        """Return available camera DeviceInfo records."""

        getter = getattr(self._device_cls, "getDeviceList", None)
        if getter is None:
            raise RuntimeError("MechEyeAPI.Device.getDeviceList not found; SDK version unsupported.")

        try:
            infos = getter()
        except TypeError:
            container: list[Any] = []
            result = getter(container)  # type: ignore[arg-type]
            if container:
                infos = container
            else:
                infos = result or []

        if infos is None:
            infos = []
        return list(infos)

    def connect(self, *, serial: Optional[str] = None, ip: Optional[str] = None, index: int = 0) -> Any:
        """Connect to a camera via serial number, IP address, or index."""

        infos = self.discover()
        target_info: Any | None = None
        if serial:
            for info in infos:
                serial_attr = getattr(info, "serialNumber", None) or getattr(info, "serial", None)
                if serial_attr == serial:
                    target_info = info
                    break
            if target_info is None:
                raise RuntimeError(f"No MechEye device with serial {serial} found.")
        elif ip:
            target_info = ip
        elif infos:
            try:
                target_info = infos[index]
            except IndexError as exc:
                raise RuntimeError(f"Device index {index} out of range for {len(infos)} devices.") from exc
        else:
            raise RuntimeError("No MechEye devices detected.")

        status = None
        if target_info in (ip,):
            status = self._attempt_connect_with_ip(ip or "")
        else:
            status = self._attempt_connect_with_info(target_info)

        self._check_status(status)
        LOG.info("Connected to MechEye camera: %s", self._describe_device(target_info))
        return target_info

    def _attempt_connect_with_info(self, info: Any) -> Any:
        for attr in ("connect", "connectByDeviceInfo", "connect_device"):
            fn = getattr(self._device, attr, None)
            if callable(fn):
                return fn(info)
        raise RuntimeError("MechEye Device has no connect method compatible with DeviceInfo.")

    def _attempt_connect_with_ip(self, ip: str) -> Any:
        for attr in ("connectByIPAddress", "connectByIp", "connectByIP", "connect_ip"):
            fn = getattr(self._device, attr, None)
            if callable(fn):
                return fn(ip)
        raise RuntimeError("MechEye Device has no connect-by-IP method; provide a serial instead.")

    def _check_status(self, status: Any) -> None:
        if status is None:
            return
        if hasattr(status, "isOK") and callable(status.isOK):
            if not status.isOK():
                message = getattr(status, "errorMessage", lambda: "unknown error")
                raise RuntimeError(f"MechEye call failed: {message() if callable(message) else message}")
        elif hasattr(status, "ok"):
            if not getattr(status, "ok"):
                message = getattr(status, "message", "unknown error")
                raise RuntimeError(f"MechEye call failed: {message}")

    def _describe_device(self, info: Any) -> str:
        parts: list[str] = []
        for name in ("modelName", "deviceName", "model"):
            value = getattr(info, name, None)
            if value:
                parts.append(str(value))
                break
        for name in ("serialNumber", "serial"):
            value = getattr(info, name, None)
            if value:
                parts.append(f"SN={value}")
                break
        for name in ("ipAddress", "ip"):
            value = getattr(info, name, None)
            if value:
                parts.append(f"IP={value}")
                break
        return " ".join(parts) if parts else repr(info)

    # --------------------------------------------------------------------- #
    # Capture + persistence
    # --------------------------------------------------------------------- #

    def capture_once(self) -> CaptureResult:
        """Capture and persist a single 2D/3D frame pair."""

        frame_2d = self._frame2d_cls() if self._frame2d_cls else None
        frame_3d = self._frame3d_cls() if self._frame3d_cls else None

        # Attempt combined capture if available.
        if self._invoke_device_method("capture", frame_2d, frame_3d):
            pass
        else:
            if frame_2d:
                self._invoke_device_method(
                    ["capture_2d", "capture2D", "captureColorMap", "captureRGBMap"], frame_2d
                )
            if frame_3d:
                self._invoke_device_method(
                    ["capture_3d", "capture3D", "capturePointMap", "captureDepthMap"], frame_3d
                )

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        color_path = self._persist_color(frame_2d, timestamp)
        depth_path = self._persist_depth(frame_3d, timestamp)
        cloud_path = self._persist_point_cloud(frame_3d, timestamp)
        return CaptureResult(color_path=color_path, depth_path=depth_path, point_cloud_path=cloud_path)

    def _invoke_device_method(self, candidates: Iterable[str] | str, *args: Any) -> bool:
        names = [candidates] if isinstance(candidates, str) else list(candidates)
        for name in names:
            fn = getattr(self._device, name, None)
            if callable(fn):
                fn(*(arg for arg in args if arg is not None))
                return True
        return False

    def _persist_color(self, frame: Any, tag: str) -> Optional[Path]:
        if frame is None:
            return None
        path = self.output_dir / f"{tag}_color.png"
        for attr in ("saveColorMap", "save_color_map", "saveRGBImage", "save"):
            fn = getattr(frame, attr, None)
            if callable(fn):
                fn(str(path))
                return path
        array = self._extract_array(frame, field_candidates=("colorMap", "rgbMap", "image"))
        if array is None:
            return None
        if cv2 is None:
            np.save(path.with_suffix(".npy"), array)  # type: ignore[arg-type]
            return path.with_suffix(".npy")
        # Frame data is typically RGB; OpenCV expects BGR.
        cv2.imwrite(str(path), array[:, :, ::-1])
        return path

    def _persist_depth(self, frame: Any, tag: str) -> Optional[Path]:
        if frame is None:
            return None
        path = self.output_dir / f"{tag}_depth.tiff"
        for attr in ("saveDepthMap", "save_depth_map", "saveZMap"):
            fn = getattr(frame, attr, None)
            if callable(fn):
                fn(str(path))
                return path
        array = self._extract_array(frame, field_candidates=("depthMap", "zMap"))
        if array is None:
            return None
        if cv2 is None:
            np.save(path.with_suffix(".npy"), array)  # type: ignore[arg-type]
            return path.with_suffix(".npy")
        cv2.imwrite(str(path), array)
        return path

    def _persist_point_cloud(self, frame: Any, tag: str) -> Optional[Path]:
        if frame is None:
            return None
        path = self.output_dir / f"{tag}_cloud.ply"
        for attr in ("savePointCloud", "save_point_cloud", "savePLY", "exportPointCloud"):
            fn = getattr(frame, attr, None)
            if callable(fn):
                fn(str(path))
                return path
        array = self._extract_array(frame, field_candidates=("pointMap", "xyzMap"))
        if array is None:
            return None
        np = self._require_numpy()
        np.savetxt(str(path.with_suffix(".xyz")), array.reshape(-1, array.shape[-1]))
        return path.with_suffix(".xyz")

    def _extract_array(self, frame: Any, field_candidates: Sequence[str]) -> Optional["np.ndarray"]:
        if np is None:
            return None
        for field in field_candidates:
            data = getattr(frame, field, None)
            if data is None:
                continue
            # Many MechEye structures expose numpy interface directly.
            if hasattr(data, "__array__"):
                array = np.asarray(data)  # type: ignore[call-arg]
                if array.size:
                    return array
            getter = getattr(data, "to_numpy", None)
            if callable(getter):
                array = getter()
                if array is not None:
                    return array
            buffer_attr = getattr(data, "buffer", None)
            if buffer_attr is not None and hasattr(buffer_attr, "__array__"):
                array = np.asarray(buffer_attr)  # type: ignore[call-arg]
                if array.size:
                    return array
        return None

    def _require_numpy(self) -> "np":
        if np is None:
            raise RuntimeError("numpy is required to save point data but is not installed.")
        return np


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture a single frame from a MechEye structured-light camera.")
    parser.add_argument("--serial", help="Preferred camera serial number.")
    parser.add_argument("--ip", help="Camera IP address (used if serial is not supplied).")
    parser.add_argument("--index", type=int, default=0, help="Fallback device index when serial/IP are not provided.")
    parser.add_argument(
        "--output-dir",
        default=str(Path("runs") / "mecheye"),
        help="Directory where captures will be written.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Logging verbosity.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s %(levelname)s %(message)s")

    capture = MechEyeCapture(output_dir=args.output_dir)
    capture.connect(serial=args.serial, ip=args.ip, index=args.index)
    result = capture.capture_once()
    LOG.info(
        "Capture finished. color=%s depth=%s cloud=%s",
        result.color_path,
        result.depth_path,
        result.point_cloud_path,
    )


if __name__ == "__main__":
    main()
