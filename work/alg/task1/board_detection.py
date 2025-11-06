from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np

from .annotations import BoundingBox, load_labelimg_boxes
from .config import TaskConfig
from .models import DownsampledCloud


@dataclass(slots=True)
class BoardDetectionResult:
    """保存板面/夹具检测阶段产生的掩膜与中间结果。"""

    board_mask_full: np.ndarray
    board_main_region_full: np.ndarray
    board_residual_full: np.ndarray
    fixture_mask_full: np.ndarray
    board_rect_points: np.ndarray
    base_height_map: np.ndarray
    board_mask_down: np.ndarray
    fixture_mask_down: np.ndarray
    bounding_boxes: List[BoundingBox]
    z_image: np.ndarray


FIT_OVERLAY_NAME = "board_fit_overlay.png"
TEXTURE_IMAGE_NAME = "src_IMG_Texture_8Bit.png"


def _save_fit_overlay(config: TaskConfig, mask: np.ndarray) -> None:
    """在纹理图上叠加主板拟合区域并输出调试截图。"""
    output_dir = Path(config.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        return

    texture_path = Path(config.source_dir) / TEXTURE_IMAGE_NAME
    if not texture_path.exists():
        return

    image = cv2.imread(str(texture_path), cv2.IMREAD_COLOR)
    if image is None:
        return

    h, w = mask.shape
    if image.shape[:2] != (h, w):
        image = cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)

    overlay = image.copy()
    mask_bool = mask.astype(bool)
    highlight = np.zeros_like(overlay, dtype=np.uint8)
    highlight[..., 1] = 255  # green
    alpha = 0.45
    overlay[mask_bool] = cv2.addWeighted(image[mask_bool], 1 - alpha, highlight[mask_bool], alpha, 0.0)

    output_path = output_dir / FIT_OVERLAY_NAME
    try:
        cv2.imwrite(str(output_path), overlay)
    except Exception:
        pass


def _load_fixture_mask_and_boxes(config: TaskConfig, shape: Tuple[int, int]) -> Tuple[np.ndarray, List[BoundingBox]]:
    """优先读取 LabelImg XML 标注，若缺失则退回遮罩图像并生成夹具掩膜。"""
    import cv2
    import numpy as np

    def _boxes_to_mask(boxes: List[BoundingBox]) -> np.ndarray:
        return _mask_from_boxes(shape, boxes)

    # Resolve candidate path
    if config.fixture_annotation:
        ann_path = Path(config.fixture_annotation)
    else:
        ann_path = Path("configs") / "calibration" / "src_IMG_Color.xml"
        if not ann_path.exists():
            # Try common color image names in the capture folder
            png = config.source_dir / "src_IMG_Color.png"
            tif = config.source_dir / "src_IMG_Color.tif"
            ann_path = png if png.exists() else (tif if tif.exists() else ann_path)

    suffix = ann_path.suffix.lower()
    if suffix == ".xml":
        boxes = load_labelimg_boxes(ann_path)
        mask = _boxes_to_mask(boxes)
        return mask, boxes

    # Load as image-based mask
    if not ann_path.exists():
        raise FileNotFoundError(f"Fixture annotation not found: {ann_path}")
    img = cv2.imread(str(ann_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"Unable to read fixture image: {ann_path}")
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img.astype(np.uint8)
    # If not already binary, apply Otsu to get a mask
    unique_vals = np.unique(img)
    if unique_vals.size <= 2:
        mask = img > 0
    else:
        _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        mask = thresh > 0

    # Derive bounding boxes from connected components (for downstream visuals)
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes: List[BoundingBox] = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h < 10:
            continue
        boxes.append(BoundingBox(name="fixture", xmin=int(x), ymin=int(y), xmax=int(x + w), ymax=int(y + h)))
    return mask.astype(bool), boxes


def _mask_from_boxes(shape: Tuple[int, int], boxes: List[BoundingBox]) -> np.ndarray:
    """将标注矩形光栅化为布尔掩膜。"""
    mask = np.zeros(shape, dtype=bool)
    for box in boxes:
        xmin = max(0, min(shape[1] - 1, box.xmin))
        xmax = max(0, min(shape[1], box.xmax))
        ymin = max(0, min(shape[0] - 1, box.ymin))
        ymax = max(0, min(shape[0], box.ymax))
        if xmin >= xmax or ymin >= ymax:
            continue
        mask[ymin:ymax, xmin:xmax] = True
    return mask


def _threshold_board(z_image: np.ndarray, fixture_mask_xml: np.ndarray, valid_depth: np.ndarray, board_base: float) -> np.ndarray:
    """根据板面基准高度，在夹具标注区域内自动滤除高于阈值的像素。"""
    board_mask = valid_depth.copy()
    inside_xml = fixture_mask_xml & valid_depth
    if np.any(inside_xml):
        diff = np.abs(z_image - board_base)
        board_mask[inside_xml] = diff[inside_xml] <= CLAMP_HEIGHT_DELTA
    return board_mask


def _refine_fixture_mask(z_image: np.ndarray, fixture_mask_xml: np.ndarray, valid_depth: np.ndarray, board_base: float) -> np.ndarray:
    """利用高度差判定夹具区域（限于 XML 标注范围）。"""
    inside_xml = fixture_mask_xml & valid_depth
    if not np.any(inside_xml):
        return np.zeros_like(valid_depth, dtype=bool)
    diff = np.abs(z_image - board_base)
    fixture_mask = np.zeros_like(valid_depth, dtype=bool)
    fixture_mask[inside_xml] = diff[inside_xml] > CLAMP_HEIGHT_DELTA
    return fixture_mask


def _compute_board_rectangle(board_mask: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """计算包围板面掩膜的最小外接矩形及其填充区域。"""
    board_uint8 = (board_mask.astype(np.uint8)) * 255
    contours, _ = cv2.findContours(board_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise RuntimeError("Unable to compute board rectangle: no contours found.")
    largest = max(contours, key=cv2.contourArea)
    rect = cv2.minAreaRect(largest)
    box = cv2.boxPoints(rect)
    box = np.intp(box)
    rect_mask = np.zeros_like(board_uint8)
    cv2.drawContours(rect_mask, [box], -1, 255, thickness=cv2.FILLED)
    return box.astype(np.float32), rect_mask.astype(bool)


def _compute_base_height_map(z_image: np.ndarray, region_mask: np.ndarray, kernel_size: int) -> np.ndarray:
    """在指定区域内执行高斯加权，估计平滑基准面。"""
    mask = region_mask
    if kernel_size % 2 == 0:
        kernel_size += 1
    values = np.where(mask, z_image, 0.0).astype(np.float32)
    weights = mask.astype(np.float32)
    blur_values = cv2.GaussianBlur(values, (kernel_size, kernel_size), 0)
    blur_weights = cv2.GaussianBlur(weights, (kernel_size, kernel_size), 0)
    base = np.zeros_like(z_image, dtype=np.float32)
    valid = blur_weights > 1e-6
    base[valid] = blur_values[valid] / blur_weights[valid]
    base[~mask] = 0.0
    return base


def _downsample_mask(mask: np.ndarray, step: int) -> np.ndarray:
    """按整数步长下采样布尔掩膜。"""
    return mask[::step, ::step]


def detect_board_and_fixtures(config: TaskConfig, cloud: DownsampledCloud) -> BoardDetectionResult:
    """执行板面、夹具检测，并生成基面高度及调试数据。"""
    z_image = cloud.zs
    reference = config.reference_plane_z
    z_image = np.where(z_image > reference, 0.0, z_image)
    valid_depth = z_image > 0
    fixture_mask_xml, boxes = _load_fixture_mask_and_boxes(config, z_image.shape)

    board_base_candidates = z_image[(~fixture_mask_xml) & valid_depth]
    if board_base_candidates.size == 0:
        board_base_candidates = z_image[valid_depth]
    board_base = float(np.median(board_base_candidates)) if board_base_candidates.size else 0.0

    fixture_mask = _refine_fixture_mask(z_image, fixture_mask_xml, valid_depth, board_base)
    board_mask = _threshold_board(z_image, fixture_mask_xml, valid_depth, board_base)

    board_without_fixture = board_mask & ~fixture_mask
    board_main_region = board_without_fixture.copy()
    if not np.any(board_main_region):
        board_main_region = board_without_fixture
    base_map = _compute_base_height_map(z_image, board_main_region, config.board_base_blur_kernel)

    reference_height = float(getattr(config, "board_mask_reference_height", 1800.0))
    board_residual_full = np.zeros_like(z_image, dtype=np.float32)
    board_residual_full[valid_depth] = np.clip(reference_height - z_image[valid_depth], 0.0, reference_height)

    try:
        board_rect_points, _ = _compute_board_rectangle(board_mask)
    except RuntimeError:
        board_rect_points = np.zeros((4, 2), dtype=np.float32)

    step = max(1, cloud.step)
    board_mask_down = _downsample_mask(board_main_region, step)
    fixture_mask_down = _downsample_mask(fixture_mask, step)

    _save_fit_overlay(config, board_main_region)

    return BoardDetectionResult(
        board_mask_full=board_without_fixture,
        board_main_region_full=board_main_region,
        board_residual_full=board_residual_full,
        fixture_mask_full=fixture_mask,
        board_rect_points=board_rect_points,
        base_height_map=base_map,
        board_mask_down=board_mask_down,
        fixture_mask_down=fixture_mask_down,
        bounding_boxes=boxes,
        z_image=z_image,
    )
