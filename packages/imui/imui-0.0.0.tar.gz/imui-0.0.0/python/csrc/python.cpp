#include <nanobind/nanobind.h>
#include <imgui/imgui.h>

namespace nb = nanobind;

namespace pyimgui {

NB_MODULE(_C, m) {
    m.attr("IMGUI_VERSION") = IMGUI_VERSION;
    m.attr("IMGUI_VERSION_NUM") = IMGUI_VERSION_NUM;
}

} // namespace pyimgui