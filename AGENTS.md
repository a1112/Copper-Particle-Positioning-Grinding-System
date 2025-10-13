# Repository Guidelines

## 项目结构与模块组织
核心代码集中在 `app/` 目录，`core/` 负责事件与状态机，`devices/` 封装真实及模拟设备驱动，`process/` 管理磨削流程，`vision/` 承担标定与视觉检测，`ui/` 提供 PySide6/QML 界面。`app/api/` 暴露 FastAPI 与 WebSocket 接口，启动脚本位于 `app/server/run_api.py`。标定与示例配置放在 `configs/`、`TestData/`，运行日志写入 `runs/`，自动化脚本存放在 `scripts/`。

## 构建、测试与开发命令
使用 `python -m venv .venv` 创建虚拟环境，`. .venv/Scripts/Activate.ps1` 激活后执行 `pip install -r requirements.txt` 安装依赖。`python -m app.main` 启动完整模拟与 UI，若只需控制 API 可运行 `python -m app.server.run_api`。UI 资源更新后请执行 `powershell -File scripts/build_rcc.ps1`，模拟环境冒烟测试可调用 `python scripts/smoke_api.py`。

## 编码风格与命名约定
遵循 PEP 8，统一使用 4 空格缩进，公开接口补充类型注解，模块与函数采用 `snake_case`，类名保持 `PascalCase`。QML 组件文件名首字母大写（如 `LineChart.qml`），对外属性通过 alias 暴露，尽量减少命令式 JavaScript。仓库未配置自动格式化，建议提交前本地运行 `black` 或 `ruff format`。

## 测试指南
目前自动化覆盖有限，`tests/ws_logs_demo.py` 主要验证 WebSocket 流程，合并前需确保脚本可用。新增功能请在 `tests/` 目录创建 pytest 风格文件（`test_<feature>.py`），重点覆盖流程编排、设备驱动及 API 协议。集成新设备时应在 `TestData/` 添加可复现数据，并在 PR 说明关键遥测指标与验证结果。

## 提交与合并规范
推荐使用 Conventional Commits（如 `feat(ui):`、`fix(core):`、`chore:`），标题保持祈使语并在 72 字符内，合并前压缩零散 WIP 提交。PR 描述需概括行为变更、关联需求或问题编号，对 UI/QML 调整附带截图或 GIF，并明确模拟环境与真机的验证步骤及结果。

## 配置与资源管理
模拟默认配置位于 `configs/`，请复制模板再修改本地路径，避免直接改动原始文件。标定图像与数据放置在 `TestData/` 并使用相对路径引用以便迁移。提交日志或运行记录前务必脱敏，移除设备序列号、坐标等敏感信息。
