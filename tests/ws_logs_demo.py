from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import urllib.request
from typing import Any

import websockets


HOST = os.getenv("COPPER_API_HOST", "127.0.0.1")
PORT = int(os.getenv("COPPER_API_PORT", "8010"))


async def main() -> int:
    url = f"ws://{HOST}:{PORT}/ws/logs"
    print(f"[demo] connecting {url}")
    async with websockets.connect(url) as ws:
        # Receive history
        msg = await ws.recv()
        try:
            data = json.loads(msg)
        except Exception:
            print("[demo] non-JSON message:", msg)
            data = {}
        items = data.get("items", []) if isinstance(data, dict) else []
        print(f"[demo] history items: {len(items)}")

        # Trigger 3 test logs via HTTP POST /test/log
        for i in range(3):
            m = f"demo-log-{i}-{int(time.time())}"
            req = urllib.request.Request(
                url=f"http://{HOST}:{PORT}/test/log?msg={urllib.parse.quote(m)}",
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                _ = resp.read()
            print(f"[demo] sent test log: {m}")
            # Read appended item
            msg2 = await ws.recv()
            try:
                data2: Any = json.loads(msg2)
            except Exception:
                print("[demo] non-JSON append:", msg2)
                continue
            if isinstance(data2, dict) and data2.get("type") == "append":
                item = data2.get("item", {})
                print(f"[demo] append <- {item.get('level')} {item.get('name')}: {item.get('msg')}")
            else:
                print("[demo] recv:", data2)

    return 0


if __name__ == "__main__":
    try:
        rc = asyncio.run(main())
        raise SystemExit(rc)
    except KeyboardInterrupt:
        print("[demo] interrupted")
        sys.exit(130)

