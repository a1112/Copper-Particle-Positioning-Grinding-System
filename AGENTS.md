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

