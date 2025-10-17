# Copper UI C++ Stub Project

This directory now contains a small Qt Quick application that mirrors the
existing Python UI by loading the same QML bundle. It is meant as a starting
point for a future C++ backend, so only placeholder logic is implemented.

## Quick Start
- Install Qt 6 (tested with 6.2+) and ensure `CMAKE_PREFIX_PATH` points to the Qt install.
- Configure the project from the repository root:
  ```powershell
  cmake -S app/ui -B app/ui/build-cpp -G "Ninja"
  cmake --build app/ui/build-cpp
  ```
- In Qt Creator, use “Open Project…” and select `app/ui/CMakeLists.txt`. Choose a Qt kit, configure, and build the `copper_ui_cpp` target.

The generated executable loads all QML/UI assets from `qml.qrc` and `resource.qrc`
and exposes stubbed context objects (`backend`, `settings`, `pyHighlighter`) so
that screens render without wiring the real Python backend.
