# Repository Guidelines

## Project Structure & Module Organization
- Core code lives in `app/`: `core/` (events, state machine), `devices/` (real/sim drivers), `process/` (grinding flows), `vision/` (calibration, inspection), `ui/` (PySide6/QML).
- API is exposed via `app/api/` (FastAPI + WebSocket). API entry: `app/server/run_api.py`.
- Configs and sample data: `configs/`, `TestData/`. Runtime logs: `runs/`. Automation scripts: `scripts/`. Tests: `tests/`.

## Build, Test, and Development Commands
- Create venv and install deps:
  `python -m venv .venv` then `. .venv/Scripts/Activate.ps1` and `pip install -r requirements.txt`.
- Run full simulator + UI: `python -m app.main`.
- Run API only: `python -m app.server.run_api`.
- Rebuild UI resources after QML/asset changes: `powershell -File scripts/build_rcc.ps1`.
- Smoke test (simulated env): `python scripts/smoke_api.py`.
- Run tests: `pytest` (or `python -m pytest`). Add files as `tests/test_<feature>.py`.

## Coding Style & Naming Conventions
- PEP 8, 4-space indent; add type hints for public interfaces.
- `snake_case` for modules/functions; `PascalCase` for classes.
- QML: component filenames Capitalized (e.g., `LineChart.qml`); expose public properties via `alias`; minimize imperative JavaScript.
- Formatting: run `black` or `ruff format` before commit.

## Testing Guidelines
- Focus on flow orchestration, device drivers, and API protocol. Keep `tests/ws_logs_demo.py` working for WebSocket flow.
- Place reproducible artifacts in `TestData/` and reference with relative paths.
- When adding devices, include sample data and note key telemetry/validation results in the PR.

## Commit & Pull Request Guidelines
- Conventional Commits: `feat(ui): ...`, `fix(core): ...`, `chore: ...`; imperative titles, <= 72 chars.
- Squash WIP commits; describe behavior changes; link issues/requirements.
- For UI/QML changes, attach screenshots or GIFs; list simulation and hardware validation steps and results.
- Sanitize logs and runs before committing (remove serials, coordinates, other sensitive data).

## Configuration & Tips
- Copy templates in `configs/` before editing local paths; do not change originals.
- Prefer relative paths for portability; runtime logs are written to `runs/`.
