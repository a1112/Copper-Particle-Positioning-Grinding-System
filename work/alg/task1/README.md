# Task 1 - Copper Particle Path Planning

This module operates in pixel space using `D:\SaveData\current\src_IMG_PointCloud_Z.tif` and fixture annotations from `configs/calibration/src_IMG_Color.xml`. The workflow is:

1. Pixels with `Z > reference_plane_z` (default 1765 mm) are set to zero to mark missing depth.
2. For remaining pixels compute `height_abs = |Z - reference_plane_z|`, giving the convex height relative to the chosen plane.
3. A smoothed base surface is estimated on the board mask; fixture rectangles from the XML are drawn as overlays (no solid fill). Relative protrusion for machining is `height_rel = base_z - Z`.
4. Pixels with `height_rel >= particle_keep_height` (default 2 mm) outside fixture masks are clustered as particle regions. Toolpaths are planned on the pixel grid for an 80 mm cutter and mapped back to point-cloud coordinates.

## Quick Start

```bash
python -m work.alg.task1.main \
  --source-dir D:\SaveData\current \
  --output-dir D:\SaveData\current\alg_task1 \
  --reference-plane-z 1765 \
  --height-display-max 100 \
  --particle-height 0.8 \
  --tool-diameter 80.0
```

## Outputs (`D:\SaveData\current\alg_task1\`)

| File | Description |
| ---- | ----------- |
| `task1_result.json` | Configuration, board metrics, fixture/particle tables, and path summary (`total_segments`, `cut_segment_count`, `cut_segments.npy`). |
| `cut_segments.npy` | Array of cutting moves: start XYZ, end XYZ, feed, cluster_id, pass_index. |
| `height_jet.png` / `height_contours.png` | Jet colormap and 1 mm colour-coded contour overlay using `reference_plane_z` directly on `Z`. |
| `particle_mask.png` | Binary mask for detected particles. |
| `board_fixture_map.png` | Board fill (blue) with fixture rectangles outlined in red. |
| `board_mask.tif` / `fixture_mask.png` | Board residual map (float) and binary fixture mask. |
| `base_height_map.tif` | Smoothed base surface (fixture pixels removed). |
| `z_without_fixtures.tif` | Depth map with fixture pixels set to zero. |
| `spindle_path.png`, `spindle_path.npy` | Spindle centre-line image and numeric path list (`[x, y, z, feed, cluster, pass, kind]`). |

Re-run `python -m work.alg.task1.main` with different parameters whenever you need to regenerate the dataset.

