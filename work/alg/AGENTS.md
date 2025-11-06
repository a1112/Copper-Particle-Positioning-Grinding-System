# Repository Guidelines

## Project Structure & Module Organization
- Core runtime lives in `app/`; keep orchestration under `app/process/`, device drivers in `app/devices/`, and the state machine in `app/core/`.
- UI and QML assets reside in `app/ui/`, calibration and inspection flow in `app/vision/`, and the FastAPI surface is launched from `app/server/run_api.py`.
- Store configuration samples in `configs/`, deterministic telemetry in `TestData/`, transient run artifacts under `runs/`, automation helpers in `scripts/`, and tests in `tests/`.

## Build, Test, and Development Commands
- Create a virtual environment: `python -m venv .venv` then `. .venv/Scripts/Activate.ps1`.
- Install dependencies: `pip install -r requirements.txt`.
- Launch the full simulator + UI for end-to-end checks: `python -m app.main`.
- Run API services only: `python -m app.server.run_api`.
- Rebuild QML resources when assets change: `powershell -File scripts/build_rcc.ps1`.
- Execute the smoke API probe: `python scripts/smoke_api.py`; run all tests with `python -m pytest`.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation and add type hints on public functions and methods.
- Use `snake_case` for Python modules, functions, and files; reserve `PascalCase` for classes and QML components.
- Format Python code with `black` or `ruff format`; keep QML declarative and prefer `alias` for exposed properties.

## Testing Guidelines
- Primary test runner is `pytest`; name new suites `tests/test_<feature>.py`.
- Prefer deterministic fixtures from `TestData/` and document any new telemetry captured from hardware.
- Ensure WebSocket flows keep passing `tests/ws_logs_demo.py`; run `python scripts/smoke_api.py` after workflow changes.

## Commit & Pull Request Guidelines
- Use Conventional Commits (e.g., `feat(ui): add drag handle`, `fix(core): guard idle transition`) and squash WIP branches.
- Describe behavioral changes, link issues or requirements, and include simulator or hardware validation notes.
- For UI/QML updates, attach screenshots or GIFs and confirm QML assets were rebuilt when relevant.

## Security & Configuration Tips
- Do not edit templates under `configs/`; copy them locally and keep paths relative.
- Sanitize `runs/` outputs before pushing and audit logs for sensitive data.
- When introducing new devices, capture representative telemetry in `TestData/` and record validation steps in the PR.
