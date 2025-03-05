cmake_minimum_required(VERSION 3.8)
project(rosidl_protozero_cmake)

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package(
        CONFIG_EXTRAS "rosidl_protozero_cmake-extras.cmake"
)

install(
        DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/cmake"
        DESTINATION "share/${PROJECT_NAME}"
)
