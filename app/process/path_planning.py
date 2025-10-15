from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class CutParams:
    step_over: float = 2.0  # mm between raster lines
    feed_mm_min: float = 800.0
    plunge_ramp_len: float = 5.0  # mm for ramp-in distance
    z_safe: float = 5.0
    d_min: float = 0.1  # mm per pass at high density
    d_max: float = 0.6  # mm per pass at low density
    height_threshold: float = 0.02  # minimum height considered as particle


@dataclass
class Segment:
    kind: str  # 'rapid' | 'ramp' | 'cut'
    pts: List[Tuple[float, float, float]]  # list of (x,y,z)


@dataclass
class ToolPath:
    segments: List[Segment]


def generate_test_heightmap(
    size: Tuple[int, int] = (200, 200),
    pixel_mm: float = 0.2,
    seed: int | None = 42,
    n_blobs: int = 25,
    clustered_ratio: float = 0.4,
) -> tuple[np.ndarray, float]:
    """
    Generate a synthetic heightmap: mostly flat, with discrete particles (blobs)
    varying in area and height. Returns (heightmap_mm, pixel_mm).
    """
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    h, w = size
    height = np.zeros((h, w), dtype=np.float32)

    # Blob centers: some uniform, some concentrated around a few cluster centers
    n_cluster_centers = max(1, int(0.2 * n_blobs))
    centers = []
    cluster_centers = rng.uniform(low=[0.2 * w, 0.2 * h], high=[0.8 * w, 0.8 * h], size=(n_cluster_centers, 2))
    for i in range(n_blobs):
        if rng.random() < clustered_ratio and n_cluster_centers > 0:
            c_idx = rng.integers(0, n_cluster_centers)
            cx, cy = cluster_centers[c_idx]
            # spread around cluster center
            cx = float(np.clip(rng.normal(cx, 0.07 * w), 0, w - 1))
            cy = float(np.clip(rng.normal(cy, 0.07 * h), 0, h - 1))
        else:
            cx = float(rng.uniform(0, w - 1))
            cy = float(rng.uniform(0, h - 1))
        centers.append((cx, cy))

    # Draw Gaussian bumps as particles with varied size/height
    yy, xx = np.mgrid[0:h, 0:w]
    for (cx, cy) in centers:
        sigma = float(rng.uniform(2.0, 10.0))  # pixels (~ area)
        amp = float(rng.uniform(0.05, 0.6))  # height in mm
        g = amp * np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2.0 * sigma**2)))
        height += g.astype(height.dtype)

    # Add light noise; clip to non-negative
    height += (rng.normal(0.0, 0.005, size=height.shape)).astype(height.dtype)
    np.maximum(height, 0.0, out=height)
    return height, pixel_mm


def _local_density(mask: np.ndarray, k_size: int = 9) -> np.ndarray:
    """Compute a local density map from binary mask via box filter (no cv2 dependency)."""
    # Integral image for fast sum in windows
    m = mask.astype(np.float32)
    ii = m.cumsum(axis=0).cumsum(axis=1)
    r = k_size // 2
    h, w = m.shape
    out = np.zeros_like(m)
    for y in range(h):
        y0 = max(0, y - r)
        y1 = min(h - 1, y + r)
        for x in range(w):
            x0 = max(0, x - r)
            x1 = min(w - 1, x + r)
            A = ii[y0 - 1, x0 - 1] if (y0 - 1 >= 0 and x0 - 1 >= 0) else 0.0
            B = ii[y1, x0 - 1] if (x0 - 1 >= 0) else 0.0
            C = ii[y0 - 1, x1] if (y0 - 1 >= 0) else 0.0
            D = ii[y1, x1]
            s = D - B - C + A
            out[y, x] = s / float((y1 - y0 + 1) * (x1 - x0 + 1))
    # Normalize to [0,1]
    if out.max() > 0:
        out = out / float(out.max())
    return out


def _per_pass_depth(density01: np.ndarray, params: CutParams) -> np.ndarray:
    """Map local density [0,1] to per-pass depth d in mm (low density -> larger d)."""
    inv = 1.0 - density01
    return params.d_min + inv * (params.d_max - params.d_min)


def _region_labels(mask: np.ndarray) -> np.ndarray:
    """Simple connected components (4-connectivity) labeler returning label image (int32)."""
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    cur = 0
    # BFS flood fill
    from collections import deque

    for y in range(h):
        for x in range(w):
            if mask[y, x] and labels[y, x] == 0:
                cur += 1
                q = deque([(y, x)])
                labels[y, x] = cur
                while q:
                    yy, xx = q.popleft()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        y2 = yy + dy
                        x2 = xx + dx
                        if 0 <= y2 < h and 0 <= x2 < w and mask[y2, x2] and labels[y2, x2] == 0:
                            labels[y2, x2] = cur
                            q.append((y2, x2))
    return labels


def plan_toolpath(
    height_mm: np.ndarray,
    pixel_mm: float,
    mode: str = "discrete",  # 'discrete' (region-first) or 'concentrated' (height-first)
    params: CutParams | None = None,
) -> ToolPath:
    """
    Plan lateral-only cutting passes (no axial plunge) over the elevated areas.
    - discrete: region-first raster within each connected particle region
    - concentrated: height-first bands, scanning from high to low
    """
    params = params or CutParams()
    h, w = height_mm.shape
    mask = (height_mm >= params.height_threshold)
    density01 = _local_density(mask.astype(np.uint8), k_size=9)
    d_mm = _per_pass_depth(density01, params)

    segments: List[Segment] = []
    z_safe = params.z_safe

    def add_raster_in_bbox(x0: int, x1: int, y0: int, y1: int, z_target: float) -> None:
        nonlocal segments
        # Generate serpentine lines across X within bbox in mm coords
        x0_mm = x0 * pixel_mm
        x1_mm = x1 * pixel_mm
        y0_mm = y0 * pixel_mm
        y1_mm = y1 * pixel_mm
        if x1_mm <= x0_mm or y1_mm <= y0_mm:
            return
        step = max(pixel_mm, params.step_over)
        ys = np.arange(y0_mm, y1_mm + 1e-6, step)
        left_to_right = True
        for y_mm in ys:
            xs = (x0_mm, x1_mm) if left_to_right else (x1_mm, x0_mm)
            start = (xs[0], y_mm, z_safe)
            end = (xs[1], y_mm, z_target)
            # Rapid to start at safe Z
            segments.append(Segment("rapid", [start]))
            # Ramp-in over small distance at start of cut to avoid pure axial plunge
            ramp_len = min(params.plunge_ramp_len, abs(xs[1] - xs[0]))
            if ramp_len > 1e-3:
                # Compute ramp end point along the line
                dir_sign = 1.0 if xs[1] >= xs[0] else -1.0
                ramp_x = xs[0] + dir_sign * ramp_len
                ramp_pt = (ramp_x, y_mm, z_target)
                segments.append(Segment("ramp", [(xs[0], y_mm, z_safe), ramp_pt]))
                # Main cut segment
                segments.append(Segment("cut", [ramp_pt, (xs[1], y_mm, z_target)]))
            else:
                segments.append(Segment("cut", [(xs[0], y_mm, z_target), (xs[1], y_mm, z_target)]))
            left_to_right = not left_to_right

    if mode == "discrete":
        labels = _region_labels(mask.astype(np.uint8))
        nlab = int(labels.max())
        # Process region by region; for each, compute a target Z by averaging
        for lab in range(1, nlab + 1):
            ys, xs = np.where(labels == lab)
            if xs.size == 0:
                continue
            x0, x1 = int(xs.min()), int(xs.max())
            y0, y1 = int(ys.min()), int(ys.max())
            # Depth: use mean per-pass depth over region (denser -> smaller d)
            region_d = float(np.mean(d_mm[y0 : y1 + 1, x0 : x1 + 1]))
            # Multi-pass if needed: cut down region height in slices
            region_h = float(height_mm[y0 : y1 + 1, x0 : x1 + 1].max())
            cur = 0.0
            while cur < region_h - 1e-3:
                z_target = -(min(region_d, region_h - cur))
                add_raster_in_bbox(x0, x1, y0, y1, z_target)
                cur += region_d
    else:
        # concentrated: height-first bands; thresholds from high to low
        hmax = float(height_mm.max())
        if hmax < params.height_threshold:
            return ToolPath(segments)
        n_bands = max(3, int(np.ceil(hmax / params.d_min)))
        # Edges from high to low
        edges = np.linspace(hmax, params.height_threshold, num=n_bands, endpoint=True)
        for i in range(len(edges) - 1):
            high = edges[i]
            low = edges[i + 1]
            band_mask = (height_mm >= low) & (height_mm < high)
            if not np.any(band_mask):
                continue
            # bounding box of the band
            ys, xs = np.where(band_mask)
            x0, x1 = int(xs.min()), int(xs.max())
            y0, y1 = int(ys.min()), int(ys.max())
            # per-pass depth: use median over band
            band_d = float(np.median(d_mm[band_mask]))
            z_target = -min(band_d, high)
            add_raster_in_bbox(x0, x1, y0, y1, z_target)

    return ToolPath(segments)


def summarize_path(path: ToolPath) -> dict:
    n_seg = len(path.segments)
    n_cut = sum(1 for s in path.segments if s.kind == "cut")
    n_ramp = sum(1 for s in path.segments if s.kind == "ramp")
    length_xy = 0.0
    for s in path.segments:
        pts = s.pts
        for i in range(1, len(pts)):
            x0, y0, _ = pts[i - 1]
            x1, y1, _ = pts[i]
            length_xy += float(np.hypot(x1 - x0, y1 - y0))
    return {
        "segments": n_seg,
        "cuts": n_cut,
        "ramps": n_ramp,
        "length_mm": round(length_xy, 3),
    }

