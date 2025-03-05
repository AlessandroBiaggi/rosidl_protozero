set(_output_path "${CMAKE_CURRENT_BINARY_DIR}/rosidl_protozero_generator_cpp/${PROJECT_NAME}")

set(_generated_headers "")
set(_generated_sources "")

set(_interface_tuples "")
set(_interface_files "")
set(_dependency_files "")
set(_dependencies "")
set(_dependency_pkgs "")

foreach (_tuple ${rosidl_protozero_generate_interfaces_INTERFACE_TUPLES})
    string(REPLACE ":" "/" _abs_file ${_tuple})
    list(APPEND _interface_tuples "${_tuple}")
    list(APPEND _interface_files "${_abs_file}")
endforeach ()

foreach (_tuple ${rosidl_protozero_generate_interfaces_DEPENDENCY_TUPLES})
    string(REPLACE ":" ";" _dep_parts ${_tuple})
    list(GET _dep_parts 0 _pkg)
    list(APPEND _dependency_pkgs "${_pkg}")
endforeach ()
list(REMOVE_DUPLICATES _dependency_pkgs)

foreach(_idl_tuple ${rosidl_generate_interfaces_IDL_TUPLES})
    string(REPLACE ":" "/" _abs_idl_file ${_idl_tuple})

    if (NOT EXISTS "${_abs_idl_file}")
        message(FATAL_ERROR "the passed file '${_abs_idl_file}' doesn't exist")
    endif ()

    list(APPEND _dependency_files "${_abs_idl_file}")
    list(APPEND _dependencies "${_idl_tuple}")
endforeach()

set(target_dependencies
        "${rosidl_protozero_generator_cpp_BIN}"
        ${rosidl_protozero_generator_cpp_GENERATOR_FILES}
        "${rosidl_protozero_generator_cpp_TEMPLATE_DIR}/msg.hpp.em"
        "${rosidl_protozero_generator_cpp_TEMPLATE_DIR}/msg__tags.hpp.em"
        "${rosidl_protozero_generator_cpp_TEMPLATE_DIR}/msg__encode.hpp.em"
        "${rosidl_protozero_generator_cpp_TEMPLATE_DIR}/msg__decode.hpp.em"
        ${_interface_files} ${_dependency_files}
)

foreach (_dependency ${target_dependencies})
    if (NOT EXISTS "${_dependency}")
        message(FATAL_ERROR "Target dependency '${_dependency}' not found")
    endif ()
endforeach ()

set(generator_arguments_file "${CMAKE_CURRENT_BINARY_DIR}/rosidl_protozero_generator_cpp__arguments.json")
rosidl_protozero_write_generator_arguments(
        "${generator_arguments_file}"
        PACKAGE_NAME "${PROJECT_NAME}"
        OUTPUT_DIR "${_output_path}"
        TEMPLATE_DIR "${rosidl_protozero_generator_cpp_TEMPLATE_DIR}"
        INTERFACE_TUPLES ${_interface_tuples}
        MESSAGE_TUPLES ${rosidl_protozero_generate_interfaces_MESSAGE_TUPLES}
        DEPENDENCY_TUPLES ${rosidl_protozero_generate_interfaces_DEPENDENCY_TUPLES}
)

execute_process(
        COMMAND
        "${Python3_EXECUTABLE}" "${rosidl_protozero_generator_cpp_BIN}"
        "--generator-arguments-file" "${generator_arguments_file}" "list"
        OUTPUT_VARIABLE _generated_files
        ERROR_VARIABLE _error
        RESULT_VARIABLE _result
)

if (NOT _result EQUAL 0)
    message(FATAL_ERROR "List generated files process return code ${_result}:\n${_error}")
endif ()

string(REGEX REPLACE "[ \t\r\n]+" ";" _generated_files "${_generated_files}")

foreach (_generated_file ${_generated_files})
    string(STRIP "${_generated_file}" _generated_file)
    get_filename_component(_ext "${_generated_file}" EXT)

    if ("${_ext}" STREQUAL ".hpp")
        list(APPEND _generated_headers "${_generated_file}")
    elseif ("${_ext}" STREQUAL ".cpp")
        list(APPEND _generated_sources "${_generated_file}")
    else ()
        message(FATAL_ERROR "Invalid generated file ${_generated_file} (ext: '${_ext}')")
    endif ()
endforeach ()

add_custom_command(
        OUTPUT ${_generated_headers} ${_generated_sources}
        COMMAND Python3::Interpreter
        ARGS "${rosidl_protozero_generator_cpp_BIN}"
        "--generator-arguments-file" "${generator_arguments_file}" "generate"
        DEPENDS "${target_dependencies}"
        COMMENT "Generating C++ code for ROS interfaces"
        VERBATIM
)

set(_visibility_control_file "${_output_path}/rosidl_protozero_generator_cpp__visibility_control.hpp")
string(TOUPPER "${PROJECT_NAME}" PROJECT_NAME_UPPER)
configure_file(
        "${rosidl_protozero_generator_cpp_TEMPLATE_DIR}/rosidl_protozero_generator_cpp__visibility_control.hpp.in"
        "${_visibility_control_file}"
        @ONLY
)
list(APPEND _generated_headers "${_visibility_control_file}")

set(_target_suffix "__rosidl_protozero_generator_cpp")

add_library(
        "${rosidl_generate_interfaces_TARGET}${_target_suffix}" "${rosidl_generator_cpp_LIBRARY_TYPE}"
        "${_generated_headers}" "${_generated_sources}" "${_visibility_control_file}"
)
target_include_directories(
        "${rosidl_generate_interfaces_TARGET}${_target_suffix}" PUBLIC
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/rosidl_protozero_generator_cpp>"
        "$<INSTALL_INTERFACE:include/${PROJECT_NAME}>"
)
ament_target_dependencies(
        "${rosidl_generate_interfaces_TARGET}${_target_suffix}"
        PUBLIC
        "rosidl_protozero_runtime"
        "${_dependency_pkgs}"
)

if (NOT TARGET "${rosidl_generate_interfaces_TARGET}__rosidl_typesupport_cpp")
    message(FATAL_ERROR "${rosidl_generate_interfaces_TARGET}__rosidl_typesupport_cpp")
endif ()

target_link_libraries(
        "${rosidl_generate_interfaces_TARGET}${_target_suffix}" PUBLIC
        "${rosidl_generate_interfaces_TARGET}__rosidl_generator_cpp"
        "${rosidl_generate_interfaces_TARGET}__rosidl_typesupport_cpp"
        "${rosidl_generate_interfaces_TARGET}__rosidl_typesupport_introspection_cpp"
)

add_library("${PROJECT_NAME}::${rosidl_generate_interfaces_TARGET}${_target_suffix}" ALIAS
        "${rosidl_generate_interfaces_TARGET}${_target_suffix}"
)

set_target_properties(
        "${rosidl_generate_interfaces_TARGET}${_target_suffix}" PROPERTIES
        LINKER_LANGUAGE CXX
)
if(rosidl_generate_interfaces_LIBRARY_NAME)
    set_target_properties("${rosidl_generate_interfaces_TARGET}${_target_suffix}"
            PROPERTIES OUTPUT_NAME "${rosidl_generate_interfaces_LIBRARY_NAME}${_target_suffix}"
    )
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    if (CXX_STANDARD)
        set(_cxx_standard "${CXX_STANDARD}")
    else ()
        set(_cxx_standard 17)
    endif ()

    set_target_properties("${rosidl_generate_interfaces_TARGET}${_target_suffix}" PROPERTIES
            CXX_STANDARD "${_cxx_standard}"
            COMPILE_OPTIONS -Wall -Wextra -Wpedantic
    )
endif()

set_property(
        TARGET "${rosidl_generate_interfaces_TARGET}${_target_suffix}"
        PROPERTY DEFINE_SYMBOL "ROSIDL_PROTOZERO_GENERATOR_BUILDING_DLL_${PROJECT_NAME}"
)

add_dependencies(
        "${rosidl_generate_interfaces_TARGET}"
        "${rosidl_generate_interfaces_TARGET}${_target_suffix}"
)

if(NOT rosidl_generate_interfaces_SKIP_INSTALL)
    install(
            DIRECTORY "${_output_path}"
            DESTINATION "include/${PROJECT_NAME}"
            PATTERN "*.hpp"
    )

    # Export old-style CMake variables
    ament_export_include_directories("include/${PROJECT_NAME}")
    ament_export_libraries("${rosidl_generate_interfaces_TARGET}${_target_suffix}")

    # Export modern CMake targets
    ament_export_targets("export_${rosidl_generate_interfaces_TARGET}${_target_suffix}")

    install(
            TARGETS "${rosidl_generate_interfaces_TARGET}${_target_suffix}"
            EXPORT "export_${rosidl_generate_interfaces_TARGET}${_target_suffix}"
            ARCHIVE DESTINATION lib
            LIBRARY DESTINATION lib
            RUNTIME DESTINATION bin
    )

    ament_export_dependencies("rosidl_protozero_runtime" "${_dependency_pkgs}")
endif()

if(BUILD_TESTING AND rosidl_generate_interfaces_ADD_LINTER_TESTS)
    find_package(ament_cmake_cppcheck REQUIRED)
    ament_cppcheck(TESTNAME "cppcheck_rosidl_protozero_generated_cpp" "${_output_path}")

    find_package(ament_cmake_cpplint REQUIRED)
    get_filename_component(_cpplint_root "${_output_path}" DIRECTORY)
    ament_cpplint(
            TESTNAME "cpplint_rosidl_protozero_generated_cpp"
            # the generated code might contain longer lines for templated types
            MAX_LINE_LENGTH 999
            ROOT "${_cpplint_root}"
            "${_output_path}"
    )

    find_package(ament_cmake_uncrustify REQUIRED)
    ament_uncrustify(
            TESTNAME "uncrustify_rosidl_protozero_generated_cpp"
            # the generated code might contain longer lines for templated types
            # a value of zero tells uncrustify to ignore line length
            MAX_LINE_LENGTH 0
            "${_output_path}"
    )
endif()
