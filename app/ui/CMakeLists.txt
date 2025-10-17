cmake_minimum_required(VERSION 3.21)

project(CopperUiCpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt6 6.2 COMPONENTS Quick Qml WebSockets REQUIRED)

add_executable(copper_ui_cpp
    cpp/main.cpp
    app.rc
)

qt6_add_resources(QML_BUNDLE
    qml.qrc
    resource.qrc
)

target_sources(copper_ui_cpp PRIVATE ${QML_BUNDLE})

target_link_libraries(copper_ui_cpp
    PRIVATE Qt6::Quick Qt6::Qml Qt6::WebSockets
)

target_compile_definitions(copper_ui_cpp
    PRIVATE $<$<CONFIG:Debug>:QT_QML_DEBUG>
)

if (QT_VERSION VERSION_GREATER_EQUAL "6.5.0")
    qt_finalize_executable(copper_ui_cpp)
endif ()
