cmake_minimum_required(VERSION 3.8)
project(rosidl_protozero_adapter)

if (CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif ()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(Protobuf REQUIRED)

set(proto_dir "${CMAKE_CURRENT_SOURCE_DIR}/proto")
file(GLOB_RECURSE proto_files "${proto_dir}/*.proto")
add_library(
        "${PROJECT_NAME}__proto"
        OBJECT "${proto_files}"
)
ament_target_dependencies("${PROJECT_NAME}__proto" "Protobuf")
protobuf_generate(
        TARGET "${PROJECT_NAME}__proto"
        LANGUAGE python
        IMPORT_DIRS "${proto_dir}"
        PROTOC_OUT_DIR "${CMAKE_CURRENT_BINARY_DIR}"
)

ament_python_install_package("${PROJECT_NAME}")

if (BUILD_TESTING)
    find_package(ament_cmake_pytest REQUIRED)
    find_package(ament_lint_auto REQUIRED)
    ament_lint_auto_find_test_dependencies()
    ament_add_pytest_test(pytest test)
endif ()

ament_package(
        CONFIG_EXTRAS "rosidl_protozero_adapter-extras.cmake.in"
)

install(
        DIRECTORY
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake"
        "${CMAKE_CURRENT_SOURCE_DIR}/resource"
        "${CMAKE_CURRENT_SOURCE_DIR}/proto"
        DESTINATION "share/${PROJECT_NAME}"
)

install(
        DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/proto/rosidl_protozero"
        DESTINATION "${PYTHON_INSTALL_DIR}"
)

install(
        PROGRAMS "${CMAKE_CURRENT_SOURCE_DIR}/bin/${PROJECT_NAME}"
        DESTINATION "lib/${PROJECT_NAME}"
)
