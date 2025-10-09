from __future__ import annotations
import socket
import struct
import time
from dataclasses import dataclass
from typing import Dict, Any


def crc16(data: bytes, poly: int = 0xA001, init: int = 0xFFFF) -> int:
    """ANSI CRC16 as described in the docs (Modbus-like, little-endian).
    Returns 16-bit integer.
    """
    crc = init
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
            crc &= 0xFFFF
    return crc


@dataclass
class RetryPolicy:
    retries: int = 2
    backoff: float = 0.2
    timeout: float = 2.0


class TcpClient:
    def __init__(self, host: str, port: int, timeout: float = 2.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock: socket.socket | None = None

    def connect(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        s.connect((self.host, self.port))
        self._sock = s

    def close(self) -> None:
        if self._sock:
            try:
                self._sock.close()
            finally:
                self._sock = None

    def send(self, data: bytes) -> None:
        assert self._sock, "Socket not connected"
        self._sock.sendall(data)

    def recv(self, n: int = 4096) -> bytes:
        assert self._sock, "Socket not connected"
        return self._sock.recv(n)

    def request(self, payload: bytes, policy: RetryPolicy | None = None) -> bytes:
        policy = policy or RetryPolicy()
        last_err: Exception | None = None
        for i in range(policy.retries + 1):
            try:
                self.send(payload)
                return self.recv()
            except Exception as e:
                last_err = e
                time.sleep(policy.backoff)
        raise last_err or RuntimeError("request failed")


class Protocol:
    """Example pack/unpack according to doc pattern.
    Frame: | LEN(2) | CMD(2 ascii) | PAYLOAD(..) | CRC16(2 little-endian) |
    """

    def pack(self, cmd: str, fields: Dict[str, Any]) -> bytes:
        body = cmd.encode("ascii") + self._encode_fields(fields)
        length = len(body) + 2  # include CRC length
        frame_wo_crc = struct.pack("<H", length) + body
        crc = crc16(frame_wo_crc)
        return frame_wo_crc + struct.pack("<H", crc)

    def unpack(self, frame: bytes) -> Dict[str, Any]:
        if len(frame) < 6:
            raise ValueError("frame too short")
        length = struct.unpack_from("<H", frame, 0)[0]
        body = frame[2:-2]
        rcrc = struct.unpack_from("<H", frame, len(frame) - 2)[0]
        if crc16(frame[:-2]) != rcrc:
            raise ValueError("CRC mismatch")
        cmd = body[:2].decode("ascii", errors="ignore")
        fields = self._decode_fields(body[2:])
        return {"cmd": cmd, "fields": fields}

    # Placeholder encoders per doc types (C4/N5/N14.2/etc.)
    def _encode_fields(self, fields: Dict[str, Any]) -> bytes:
        parts: list[bytes] = []
        for k, v in fields.items():
            s = f"{k}={v};"
            parts.append(s.encode("ascii", errors="ignore"))
        return b"".join(parts)

    def _decode_fields(self, b: bytes) -> Dict[str, str]:
        txt = b.decode("ascii", errors="ignore")
        res: Dict[str, str] = {}
        for seg in txt.split(";"):
            if not seg:
                continue
            if "=" in seg:
                k, v = seg.split("=", 1)
                res[k] = v
        return res

