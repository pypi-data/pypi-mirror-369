cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)
find_package(OpenCL REQUIRED)

pybind11_add_module(core1 MODULE src/core1/main.cpp)
pybind11_add_module(core2 MODULE src/core2/main.cpp)

target_include_directories(core1 PRIVATE ${OpenCL_INCLUDE_DIRS})
target_include_directories(core2 PRIVATE ${OpenCL_INCLUDE_DIRS})
target_link_libraries(core1 PRIVATE ${OpenCL_LIBRARIES})
target_link_libraries(core2 PRIVATE ${OpenCL_LIBRARIES})
message(STATUS "OpenCL Include Directory: ${OpenCL_INCLUDE_DIRS}")
message(STATUS "OpenCL Library: ${OpenCL_LIBRARIES}")

install(TARGETS core1 core2 DESTINATION ${SKBUILD_PROJECT_NAME})
