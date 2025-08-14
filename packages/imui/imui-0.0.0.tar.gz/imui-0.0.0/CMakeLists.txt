cmake_minimum_required(VERSION 3.15)

project(imui)

set(CMAKE_CXX_STANDARD 17)

if(WIN32)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()
if(MSVC)
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL")
endif()

include_directories(${CMAKE_SOURCE_DIR})

add_subdirectory(imgui)
add_subdirectory(python)
