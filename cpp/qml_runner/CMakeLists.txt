cmake_minimum_required(VERSION 3.21)

project(qml_runner LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 6.2 REQUIRED COMPONENTS Quick Qml)

add_executable(qml_runner
  src/main.cpp
)

target_link_libraries(qml_runner PRIVATE Qt6::Quick Qt6::Qml)

if(WIN32)
  # Build as GUI app on Windows
  set_target_properties(qml_runner PROPERTIES WIN32_EXECUTABLE TRUE)
endif()

