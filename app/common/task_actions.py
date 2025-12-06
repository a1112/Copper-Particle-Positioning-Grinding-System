from __future__ import annotations

from typing import Dict, Tuple

DEFAULT_TASK_NAME = "控制指令"
DEFAULT_TASK_TYPE = 99
PARAM_UPDATE_ACTION = "params.update"

ACTION_META: Dict[str, Tuple[str, int]] = {
    "capture": ("采集", 5),
    "start": ("执行", 1),
    "run.start": ("执行", 1),
    "run.stop": ("停止", 2),
    "stop": ("停止", 2),
    "estop": ("急停", 3),
    "reset": ("初始化", 4),
    "motion.home": ("回归零位", 6),
    "motion.set_work_origin": ("设置工件原点", 7),
    "motion.jog": ("点动", 8),
    "motion.set_speed": ("设置速度", 9),
    "boost": ("性能提升", 10),
    "manual.single_frame_capture": ("单帧采集", 40),
    "manual.preprocess_roi_cluster": ("预处理(ROI+聚类)", 41),
    "manual.defect_detection": ("缺陷检测", 42),
    "manual.defect_detection_secondary": ("缺陷检测", 43),
    "manual.c5_upload": ("c5.上传指令", 44),
    "manual.run_command": ("运行指令", 45),
    "manual.clear_upload": ("清除上传的指令", 46),
    "manual.initialize": ("初始化", 47),
    "manual.initialize_secondary": ("初始化", 48),
    PARAM_UPDATE_ACTION: ("参数更新", 50),
    "cylinder.clamp_all": ("气缸全部夹紧", 51),
    "cylinder.release_all": ("气缸全部松开", 52),
    "spindle.tool_change": ("主轴换刀", 54),
    "spindle.stop": ("主轴停止", 55),
    "spindle.home_z": ("主轴Z值回零", 56),
    "chip.open": ("排屑打开", 57),
    "chip.close": ("排屑关闭", 58),
    "manual.check": ("手动点检", 61),
}


def normalise_action(action: str) -> str:
    return str(action or "").strip().lower()


def get_action_meta(action: str) -> Tuple[str, int]:
    key = normalise_action(action)
    return ACTION_META.get(key, (DEFAULT_TASK_NAME, DEFAULT_TASK_TYPE))


def friendly_action_name(action: str) -> str:
    name, _ = get_action_meta(action)
    return name


def friendly_action_type(action: str) -> int:
    _, type_code = get_action_meta(action)
    return type_code


__all__ = [
    "ACTION_META",
    "DEFAULT_TASK_NAME",
    "DEFAULT_TASK_TYPE",
    "PARAM_UPDATE_ACTION",
    "friendly_action_name",
    "friendly_action_type",
    "get_action_meta",
    "normalise_action",
]
