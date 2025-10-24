# MechEye Structured-Light Capture

This module wraps the `MechEyeAPI` SDK so we can list cameras, connect, and capture a single RGB + depth + point cloud snapshot.

## Quick Start

```bash
python -m app.vision.mecheye.capture --serial <camera-serial> --output-dir runs/mecheye
```

If you omit `--serial`, the tool tries `--ip` or falls back to the first discovered camera (`--index 0`).

Outputs are saved to the chosen directory:

- `<timestamp>_color.png` (RGB image; `.npy` fallback when OpenCV unavailable)
- `<timestamp>_depth.tiff` (depth map; `.npy` fallback)
- `<timestamp>_cloud.ply` or `.xyz` when the SDK lacks direct PLY export

Install MechEye SDK (and ensure `MechEyeAPI` is importable) before running the command.
