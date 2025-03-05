function(rosidl_protozero_convert_case_style out_var)
    find_program(ros2_EXECUTABLE "ros2" REQUIRED)

    cmake_parse_arguments(
            ARG
            "" "CASE" ""
            ${ARGN}
    )

    if (NOT ARG_CASE)
        message(FATAL_ERROR "rosidl_protozero_convert_case_style(): no case style specified")
    endif ()

    execute_process(
            COMMAND
            "${ros2_EXECUTABLE}" run
            rosidl_protozero_pycommon case_style
            --case "${ARG_CASE}"
            "${ARG_UNPARSED_ARGUMENTS}"
            OUTPUT_VARIABLE output
            ERROR_VARIABLE error
            RESULT_VARIABLE result
    )

    if (NOT result EQUAL 0)
        message(FATAL_ERROR "Process return code ${result}:\n${error}")
    endif ()

    set(${out_var} ${output} PARENT_SCOPE)
endfunction()
