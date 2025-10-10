from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from datetime import datetime


POINT_RE = re.compile(
    r"路径点(\d+).*?def-xyz=\[(\d+)\s*,\s*([-+0-9.]+)\s*,\s*([-+0-9.]+)\s*,\s*([-+0-9.]+)\].*?图像坐标\[\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\].*?避让气缸索引=\[([^\]]*)\]"
)
DETECT_MS_RE = re.compile(r"缺陷检测\s*耗时=\s*(\d+)\s*ms")
PLAN_COST_RE = re.compile(r"路径规划\s*耗时=\s*([0-9.]+)")
TS_RE = re.compile(r"^(\d{8}_\d{2}_\d{2}_\d{2})\t")


def parse_log(path: Path) -> dict:
    """解析 MFC 日志为结构化 JSON（中文注释）。

    参数：path 日志路径
    返回：{"sessions": [{timestamp, planning_cost, detection_ms, points: [...]}, ...]}
    """
    sessions: list[dict] = []
    cur: dict | None = None
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            m_ts = TS_RE.search(line)
            if "路径规划" in line:
                m = PLAN_COST_RE.search(line)
                if m:
                    # start a new session
                    cur = {
                        "timestamp": m_ts.group(1) if m_ts else None,
                        "planning_cost": float(m.group(1)),
                        "detection_ms": None,
                        "points": [],
                    }
                    sessions.append(cur)
                continue
            if "缺陷检测" in line:
                m = DETECT_MS_RE.search(line)
                if m and cur is not None:
                    cur["detection_ms"] = int(m.group(1))
                # if no current session yet, record as standalone
                elif m and cur is None:
                    cur = {
                        "timestamp": m_ts.group(1) if m_ts else None,
                        "planning_cost": None,
                        "detection_ms": int(m.group(1)),
                        "points": [],
                    }
                    sessions.append(cur)
                continue
            pm = POINT_RE.search(line)
            if pm or ("def-xyz=[" in line):
                if cur is None:
                    cur = {
                        "timestamp": m_ts.group(1) if m_ts else None,
                        "planning_cost": None,
                        "detection_ms": None,
                        "points": [],
                    }
                    sessions.append(cur)
                if pm:
                    idx = int(pm.group(1))
                    pdef = int(pm.group(2))
                    x = float(pm.group(3))
                    y = float(pm.group(4))
                    z = float(pm.group(5))
                    row = float(pm.group(6))
                    col = float(pm.group(7))
                    cyl_raw = pm.group(8)
                    cyl_list = [int(n) for n in re.findall(r"\d+", cyl_raw)]
                else:
                    # Fallback parser using bracket positions only
                    # index: try parse from Chinese tag, else incremental
                    m_idx = re.search(r"路径点(\d+)", line)
                    idx = int(m_idx.group(1)) if m_idx else len(cur["points"])
                    # def-xyz bracket
                    try:
                        a = line.index("def-xyz=[") + len("def-xyz=[")
                        b = line.index("]", a)
                        nums = [v.strip() for v in line[a:b].split(",")]
                        pdef = int(float(nums[0]))
                        x = float(nums[1])
                        y = float(nums[2])
                        z = float(nums[3])
                    except Exception:
                        continue
                    # next bracket for image coords
                    try:
                        a2 = line.index("[", b + 1) + 1
                        b2 = line.index("]", a2)
                        nums2 = [v.strip() for v in line[a2:b2].split(",")]
                        row = float(nums2[0])
                        col = float(nums2[1])
                    except Exception:
                        row = col = -1.0
                    # last bracket for cylinders
                    try:
                        al = line.rindex("[") + 1
                        bl = line.index("]", al)
                        cyl_raw = line[al:bl]
                        cyl_list = [int(n) for n in re.findall(r"\d+", cyl_raw)]
                    except Exception:
                        cyl_list = []
                cur["points"].append(
                    {
                        "index": idx,
                        "def": pdef,
                        "x": x,
                        "y": y,
                        "z": z,
                        "image_row": row,
                        "image_col": col,
                        "avoid_cylinders": cyl_list,
                    }
                )
    return {"sessions": sessions}


def main() -> None:
    """命令行入口（中文注释）：

    - 支持指定输入日志与输出目录/文件名
    - 同时导出 JSON 与 CSV
    """
    ap = argparse.ArgumentParser(description="Export LZPP path points from MFC log to JSON")
    ap.add_argument(
        "--input",
        type=Path,
        default=Path(
            "docs/铜粒子项目/算法/A001粒子打磨/MfcTestLzdmAlg/x64/Debug/Log/log.txt"
        ),
        help="Path to the MFC log.txt",
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=Path("logs/exports"),
        help="Directory to write JSON files",
    )
    ap.add_argument(
        "--name",
        type=str,
        default=None,
        help="Optional output file base name (without extension)",
    )
    args = ap.parse_args()

    data = parse_log(args.input)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = args.name or f"lzpp_export_{ts}"
    out_json = args.output_dir / f"{base}.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Also export CSV (flatten all sessions with a session index)
    out_csv = args.output_dir / f"{base}.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "session_idx",
                "timestamp",
                "planning_cost",
                "detection_ms",
                "index",
                "def",
                "x",
                "y",
                "z",
                "image_row",
                "image_col",
                "avoid_cylinders",
            ]
        )
        for si, sess in enumerate(data.get("sessions", [])):
            ts = sess.get("timestamp")
            pc = sess.get("planning_cost")
            dm = sess.get("detection_ms")
            for p in sess.get("points", []):
                w.writerow(
                    [
                        si,
                        ts,
                        pc,
                        dm,
                        p.get("index"),
                        p.get("def"),
                        p.get("x"),
                        p.get("y"),
                        p.get("z"),
                        p.get("image_row"),
                        p.get("image_col"),
                        ",".join(str(n) for n in p.get("avoid_cylinders", [])),
                    ]
                )
    print(str(out_json))
    print(str(out_csv))


if __name__ == "__main__":
    main()
