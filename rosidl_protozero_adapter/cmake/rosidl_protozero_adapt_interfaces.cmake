#
# Convert non-idl interface files into `.idl` files.
#
# The input files might be a `.proto` files.
#
# :param idl_var: the variable name to return the list of generated `.idl`
#   files, each item is a tuple separated by a colon with an absolute base path
#   and a path relative to that base path
# :type idl_var: string
# :param arguments_file: the path of the arguments file containing the paths of
#   the non-idl files.
# :type arguments_file: string
# :param TARGET: the name of the generation target
# :type TARGET: string
#
# @public
#
function(rosidl_protozero_adapt_interfaces idl_var arguments_file)
    cmake_parse_arguments(ARG "" "TARGET;OUTPUT" "" ${ARGN})

    if (ARG_UNPARSED_ARGUMENTS)
        message(FATAL_ERROR "Unknown arguments: ${ARG_UNPARSED_ARGUMENTS}")
    endif ()

    find_package(Python3 REQUIRED COMPONENTS Interpreter)

    set(idl_output "${CMAKE_CURRENT_BINARY_DIR}/rosidl_protozero_adapter/${ARG_TARGET}.idls")
    set(pkt_output "${CMAKE_CURRENT_BINARY_DIR}/rosidl_protozero_adapter/${ARG_TARGET}.pkts")
    set(spk_output "${CMAKE_CURRENT_BINARY_DIR}/rosidl_protozero_adapter/${ARG_TARGET}.spks")

    execute_process(
            COMMAND
            "${Python3_EXECUTABLE}" -m rosidl_protozero_adapter
            --package-name "${PROJECT_NAME}"
            --arguments-file "${arguments_file}"
            --output-dir "${CMAKE_CURRENT_BINARY_DIR}/rosidl_protozero_adapter/${PROJECT_NAME}"
            --idl-output-file "${idl_output}"
            --pkt-output-file "${pkt_output}"
            --spk-output-file "${spk_output}"
            --pb-output-file "${ARG_OUTPUT}"
            OUTPUT_VARIABLE output
            ERROR_VARIABLE error
            RESULT_VARIABLE result
    )

    if (NOT result EQUAL 0)
        message(FATAL_ERROR "Generate process return code ${result}:\n${error}")
    endif ()

    file(STRINGS "${idl_output}" idl_tuples)
    set(${idl_var} ${idl_tuples} PARENT_SCOPE)
endfunction()
