macro(_rosidl_protozero_cmake_register_package_hook)
    if(NOT DEFINED _ROSIDL_PROTOZERO_CMAKE_PACKAGE_HOOK_REGISTERED)
        set(_ROSIDL_PROTOZERO_CMAKE_PACKAGE_HOOK_REGISTERED TRUE)

        find_package(ament_cmake_core QUIET REQUIRED)
        ament_register_extension("ament_package" "rosidl_protozero_cmake"
                "rosidl_protozero_cmake_package_hook.cmake")

        find_package(ament_cmake_export_dependencies QUIET REQUIRED)
    endif()
endmacro()

find_package(ament_cmake QUIET REQUIRED)
find_package(rosidl_cmake QUIET REQUIRED)
find_package(rosidl_protozero_adapter QUIET REQUIRED)

find_package(std_msgs QUIET REQUIRED)
find_package(Protobuf QUIET REQUIRED COMPONENTS protoc)

ament_register_extension(
        "ament_package"
        "rosidl_protozero_cmake"
        "rosidl_protozero_cmake_package_hook.cmake"
)

include("${rosidl_protozero_cmake_DIR}/rosidl_protozero_convert_case_style.cmake")
include("${rosidl_protozero_cmake_DIR}/rosidl_protozero_write_generator_arguments.cmake")
include("${rosidl_protozero_cmake_DIR}/rosidl_protozero_generate_interfaces.cmake")
