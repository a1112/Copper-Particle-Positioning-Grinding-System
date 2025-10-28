# Repository Guidelines

## Project Structure & Module Organization
- Core runtime in `app/`.
- `app/core/`: events and state machine.
- `app/devices/`: real and simulated drivers.
- `app/process/`: grinding flow orchestration.
- `app/vision/`: calibration and inspection.
- `app/ui/`: PySide6/QML components.
- `app/api/`: public API; FastAPI entry at `app/server/run_api.py`.
- `configs/`: configuration templates and samples.
- `TestData/`: fixtures and representative telemetry.
- `runs/`: runtime artifacts (sanitize before pushing).
- `scripts/`: automation helpers.
- `tests/`: unit/integration tests.

## Build, Test, and Development Commands
- Create venv (PowerShell): `python -m venv .venv` then `. .venv/Scripts/Activate.ps1`.
- Install deps: `pip install -r requirements.txt`.
- Launch full simulator + UI: `python -m app.main`.
- Run API services only: `python -m app.server.run_api`.
- Rebuild QML assets: `powershell -File scripts/build_rcc.ps1`.
- Smoke API check: `python scripts/smoke_api.py`.
- Run tests: `python -m pytest`.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation; add type hints for public interfaces.
- Use `snake_case` for modules, functions, and file names; `PascalCase` for classes and QML (e.g., `LineChart.qml`).
- Format before committing with `black` or `ruff format`.
- Keep QML declarative: prefer `alias` for public properties; minimize imperative JS.

## Testing Guidelines
- Test runner: `pytest`. Add tests as `tests/test_<feature>.py`.
- Prefer deterministic fixtures in `TestData/`.
- Validate WebSocket flows by ensuring `tests/ws_logs_demo.py` passes.
- Confirm smoke coverage after workflow changes: `python scripts/smoke_api.py`.

## Commit & Pull Request Guidelines
- Use Conventional Commits (e.g., `feat(ui): add drag handle`, `fix(core): guard idle transition`).
- Squash WIP commits; describe behavioral changes; link issues/requirements.
- For UI/QML changes, include screenshots/GIFs and document simulator/hardware validation.
- Sanitize `runs/` outputs before pushing.

## Security & Configuration Tips
- Do not edit templates in `configs/` directly—copy locally and keep paths relative.
- Audit logs for sensitive data; avoid secrets in scripts or `TestData/`.
- When adding devices, capture representative telemetry in `TestData/` and note validation steps in the PR.

## Encoding Notes
- Store Chinese UI copy in QML/JS via `qsTr("\\uXXXX...")` so the literals stay stable across shells and locales.
- When documentation must contain raw Chinese characters, save the file as UTF-8 (no BOM) to avoid mojibake on Windows.

---

# 仓库指南

## 项目结构与模块组织
- 核心运行时位于 `app/`。
- `app/core/`：事件与状态机。
- `app/devices/`：真实与模拟驱动。
- `app/process/`：研磨流程编排。
- `app/vision/`：标定与检测。
- `app/ui/`：PySide6/QML 组件。
- `app/api/`：公共 API，FastAPI 入口为 `app/server/run_api.py`。
- `configs/`：配置模板与示例。
- `TestData/`：固定装置与代表性遥测数据。
- `runs/`：运行期产物（推送前需清理）。
- `scripts/`：自动化脚本。
- `tests/`：单元 / 集成测试。

## 构建、测试与开发命令
- 创建虚拟环境（PowerShell）：`python -m venv .venv`，然后 `. .venv/Scripts/Activate.ps1`。
- 安装依赖：`pip install -r requirements.txt`。
- 启动完整模拟器与 UI：`python -m app.main`。
- 仅运行 API 服务：`python -m app.server.run_api`。
- 重新构建 QML 资源：`powershell -File scripts/build_rcc.ps1`。
- API 冒烟检查：`python scripts/smoke_api.py`。
- 运行测试：`python -m pytest`。

## 编码风格与命名规范
- 遵循 PEP 8，使用 4 空格缩进；对公共接口添加类型提示。
- 模块、函数与文件名使用 `snake_case`；类与 QML 使用 `PascalCase`（例如 `LineChart.qml`）。
- 提交前使用 `black` 或 `ruff format` 格式化。
- 保持 QML 声明式：对外属性优先使用 `alias`，尽量减少命令式 JS。

## 测试指南
- 测试运行器：`pytest`。新增测试文件命名为 `tests/test_<feature>.py`。
- 优先使用 `TestData/` 中的确定性固定装置。
- 通过 `tests/ws_logs_demo.py` 验证 WebSocket 流程。
- 工作流变更后通过 `python scripts/smoke_api.py` 确认冒烟覆盖。

## 提交与 PR 指南
- 使用规范化提交（例如 `feat(ui): add drag handle`、`fix(core): guard idle transition`）。
- 压缩 WIP 提交；描述行为变化并关联需求 / Issue。
- UI/QML 变更需附截图或动图，并记录模拟器 / 硬件验证。
- 推送前清理 `runs/` 输出。

## 安全与配置提示
- 不要直接修改 `configs/` 模板——复制后使用相对路径。
- 审核日志，避免在脚本或 `TestData/` 中泄露敏感数据。
- 新增设备时，在 `TestData/` 中补充代表性遥测，并在 PR 中记录验证步骤。

## 编码注意事项
- QML/JS 中若需中文请使用 `qsTr("\\uXXXX...")` 的形式保存，避免在不同 Shell/操作系统 Locale 下出现乱码。
- 文档类文件如果直接书写中文，请以 UTF-8（无 BOM）编码保存，防止跨平台查看时的字符损坏。
