# 铜粒子定位磨削系统 - Python + QML 框架

## 快速开始
```
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python -m app.main
```

## 目录
- app/core: 事件总线/状态机/配方/互锁
- app/devices: 设备接口与模拟器
- app/vision: 视觉标定/检测/流水线
- app/motion: 运动规划
- app/process: 流程编排
- app/ui: QML UI 与桥接
- configs: 配方与设备/标定示例
- runs: 运行产物
- tests: 测试用例
