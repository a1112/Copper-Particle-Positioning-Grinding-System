# Task1 管线逻辑说明

以下文档用于记录 `app/vision/task1/` 模块当前的处理流程，便于日后提出或追踪需求。

## 1. 总体流程

`pipeline.run_pipeline` 依次执行：

1. **数据加载**（`data_io.load_downsampled_cloud`）：读取 `src_IMG_PointCloud_{X,Y,Z}.tif`，按 `grid_step` 下采样为 `DownsampledCloud`。
2. **板面 / 夹具检测**（`board_detection.detect_board_and_fixtures`）：利用 XML 标注和高度差，计算主板区域、夹具掩膜、基准高度图。
3. **残差计算**：下采样基准高度后，与点云高度相减得到残差图 `residual_map`。
4. **夹具提取**（`segmentation.detect_fixtures`）：结合残差与标注掩膜识别夹具，输出 `Fixture` 列表。
5. **颗粒提取**（`segmentation.detect_particles`）：在板面非夹具区域内筛选颗粒簇，并将靠近夹具的小簇合并回夹具掩膜。
6. **路径规划**（可选，`path_planner.plan_toolpaths`）：按颗粒密度生成 `rapid / plunge / cut / retract` 刀路段。
7. **可视化/导出**（`visualization.generate_visualizations` + `export`）：生成调试图层、数值摘要文件以及路径数据。

`PipelineResult` 汇总上述阶段的核心数据；若 `build_visuals=True`，还会返回可视化矩阵。

## 2. 板面与基准高度

- XML 标注区域外的像素默认视为板面。
- XML 覆盖区域内，先根据板面基准高度（来自非 XML 区域的中位值）计算与夹具的高度差。若高度差 ≥ 51 mm，则认定为夹具，否则仍属于板面。
- `board_mask_full`：纯板面掩膜（已排除夹具）。
- `board_main_region_full`：用于基面拟合的主板区域。
- `_compute_base_height_map` 仅在 `board_main_region` 内做高斯加权平滑，得到 `base_height_map`。
- `board_residual_full = clip(board_mask_reference_height - Z, 0, board_mask_reference_height)`；导出为 `board_mask.tif` 供残差分析。
- 同时生成 `board_fit_overlay.png`，展示主板区域叠加在 `src_IMG_Texture_8Bit.png` 上的调试图。

## 3. 残差、夹具与颗粒

- `residual_map = base_down - z_down`，缺失深度处置 0。
- `detect_fixtures`：若存在外部标注直接使用；否则通过残差阈值与边带宽度搜索夹具，记录质心、面积、最大高度等信息。
- `detect_particles`：在 `board_mask_down` 范围内，排除夹具，筛选满足高度和面积阈值的颗粒簇，并记录统计属性。
- `_merge_particles_into_fixtures`：将像素数不超过 `fixture_merge_particle_px` 且与夹具膨胀区相交的小簇并回夹具掩膜。

## 4. 路径规划（可选）

若需要生成刀路，`plan_toolpaths` 会：

1. 按刀具半径和安全裕量扩张夹具掩膜，得到加工禁区。
2. 为每个颗粒簇计算切削层数、步距、进给方向/速度。
3. 使用 `_contiguous_segments` 在颗粒掩膜中找连续加工区，并依次生成 `rapid → plunge → cut → retract`。
4. 输出 `ToolPathPlan`，供导出或仿真使用。

## 5. 可视化/导出

- `board_main_region.png`：`board_main_region_full` 的 0/255 掩膜。
- `board_mask.tif`：`board_residual_full` 的 float32 图，表示相对参考平面的高度差。
- `fixture_mask.png`：夹具二值掩膜。
- `board_fit_overlay.png`：主板区域叠加在彩色纹理图上的调试图。
- `height_jet.png`、`height_contours.png`：残差高度的伪彩与分层等高线。
- `particle_mask.png` / `particle_mask_overlay.png`：颗粒分布及其在彩色图中的位置。
- 其他如 `spindle_path.png/.npy`、`z_without_fixtures.tif` 等维持原有含义。

## 6. 使用提示

- 运行：`python -m app.vision.task1.main --source-dir <数据目录> --output-dir <输出目录>`。
- 若需调整高度差阈值，可修改 `particle_keep_height`、`board_mask_reference_height` 等配置。
- 新增调试图层时，可在 `visualization.generate_visualizations` 中扩展；`export.export_visuals` 会自动输出对应文件。
