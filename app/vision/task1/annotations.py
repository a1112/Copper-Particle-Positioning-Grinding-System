from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import xml.etree.ElementTree as ET


@dataclass(slots=True)
class BoundingBox:
    """LabelImg 标注中提取的轴对齐矩形。"""

    name: str
    xmin: int
    ymin: int
    xmax: int
    ymax: int

    def as_tuple(self) -> tuple[int, int, int, int]:
        """以 ``(xmin, ymin, xmax, ymax)`` 的形式返回矩形坐标。"""
        return self.xmin, self.ymin, self.xmax, self.ymax


def load_labelimg_boxes(xml_path: Path) -> List[BoundingBox]:
    """读取 LabelImg XML 文件并转换为 BoundingBox 列表。"""
    if not xml_path.exists():
        raise FileNotFoundError(f"Annotation file not found: {xml_path}")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    boxes: List[BoundingBox] = []
    for obj in root.findall("object"):
        name = obj.findtext("name", default="fixture")
        bndbox = obj.find("bndbox")
        if bndbox is None:
            continue
        xmin = int(float(bndbox.findtext("xmin", default="0")))
        ymin = int(float(bndbox.findtext("ymin", default="0")))
        xmax = int(float(bndbox.findtext("xmax", default="0")))
        ymax = int(float(bndbox.findtext("ymax", default="0")))
        boxes.append(BoundingBox(name=name, xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax))
    return boxes
