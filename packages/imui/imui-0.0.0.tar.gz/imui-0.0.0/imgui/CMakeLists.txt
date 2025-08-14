include_directories(
    ${CMAKE_SOURCE_DIR}/imgui
    ${CMAKE_SOURCE_DIR}/imgui/backends
)

add_library(
    imgui SHARED
    backends/imgui_impl_dx12.cpp
    backends/imgui_impl_win32.cpp
    imgui_draw.cpp
    imgui_tables.cpp
    imgui_widgets.cpp
    imgui.cpp
)

target_link_libraries(
    imgui PRIVATE
    d3d12.lib
    d3dcompiler.lib
    dxgi.lib
)

install(TARGETS imgui DESTINATION .)