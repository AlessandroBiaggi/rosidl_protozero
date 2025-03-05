cmake_minimum_required(VERSION 3.8)
project(rosidl_protozero_generator_cpp CXX)

if (NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 17)
endif ()

if (CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif ()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_index_register_resource("rosidl_protozero_generator_packages")

ament_python_install_package("${PROJECT_NAME}")

if (BUILD_SHARED_LIBS)
    set(${PROJECT_NAME}_LIBRARY_TYPE "SHARED")
else ()
    set(${PROJECT_NAME}_LIBRARY_TYPE "STATIC")
endif ()

install(
        PROGRAMS "${CMAKE_CURRENT_SOURCE_DIR}/bin/${PROJECT_NAME}"
        DESTINATION "lib/${PROJECT_NAME}"
)
install(
        DIRECTORY
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake"
        "${CMAKE_CURRENT_SOURCE_DIR}/resource"
        DESTINATION "share/${PROJECT_NAME}"
)

if (BUILD_TESTING)
    find_package(ament_lint_auto REQUIRED)
    ament_lint_auto_find_test_dependencies()
endif ()

ament_package(
        CONFIG_EXTRAS "${PROJECT_NAME}-extras.cmake.in"
)
