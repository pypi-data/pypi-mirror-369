nanobind_add_module(
    _C STABLE_ABI
    python.cpp
)
target_link_libraries(_C PRIVATE imgui)

install(TARGETS _C DESTINATION .)