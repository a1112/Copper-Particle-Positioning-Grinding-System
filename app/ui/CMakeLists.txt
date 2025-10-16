cmake_minimum_required(VERSION 3.16)

project(UiLauncher LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Sources
set(UILAUNCHER_SOURCES
    main.cpp
    app.rc
)

# Build a Windows GUI executable (no console window)
add_executable(UiLauncher WIN32 ${UILAUNCHER_SOURCES})

# On MSVC, ensure Unicode by default
if(MSVC)
    target_compile_definitions(UiLauncher PRIVATE UNICODE _UNICODE)
endif()

# Installation target (optional)
install(TARGETS UiLauncher RUNTIME DESTINATION bin)

