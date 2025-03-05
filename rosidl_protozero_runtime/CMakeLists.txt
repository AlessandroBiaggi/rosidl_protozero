cmake_minimum_required(VERSION 3.8)
project(rosidl_protozero_runtime)

if(NOT CMAKE_C_STANDARD)
    set(CMAKE_C_STANDARD 99)
endif()
if (NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 17)
endif ()

if (CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif ()

find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(std_msgs REQUIRED)

option(PROTOZERO_USE_VIEW "Protozero view type" "")

add_library("rosidl_protozero" INTERFACE)
set_target_properties("rosidl_protozero" PROPERTIES LINKER_LANGUAGE CXX)
target_include_directories("rosidl_protozero" INTERFACE
        # protozero
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/protozero/include>"
        "$<INSTALL_INTERFACE:include/${PROJECT_NAME}>"
        # rosidl
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
        "$<INSTALL_INTERFACE:include/${PROJECT_NAME}>"
)
ament_target_dependencies("rosidl_protozero" INTERFACE
        "builtin_interfaces"
        "std_msgs"
)

if (PROTOZERO_USE_VIEW)
    target_compile_definitions("rosidl_protozero" INTERFACE PROTOZERO_USE_VIEW="${PROTOZERO_USE_VIEW}")
endif ()

install(
        DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/protozero/include/"
        DESTINATION "include/${PROJECT_NAME}"
)
install(
        DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/include/"
        DESTINATION "include/${PROJECT_NAME}"
)

install(
        TARGETS "rosidl_protozero"
        EXPORT "export_${PROJECT_NAME}"
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin
)

ament_export_targets("export_${PROJECT_NAME}" HAS_LIBRARY_TARGET)

if (BUILD_TESTING)
    find_package(ament_lint_auto REQUIRED)
    ament_lint_auto_find_test_dependencies()
endif ()

ament_package()
