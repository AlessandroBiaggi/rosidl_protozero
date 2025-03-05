#
# Generate a JSON file containing the rosidl protozero generator arguments.
#
#
# @public
#
function(rosidl_protozero_write_generator_arguments output_file)
    set(FLAG_KEYWORDS
            ""
    )

    set(REQUIRED_ONE_VALUE_KEYWORDS
            "PACKAGE_NAME"
    )
    set(OPTIONAL_ONE_VALUE_KEYWORDS
            "OUTPUT_DIR"
            "TEMPLATE_DIR"
    )

    set(REQUIRED_MULTI_VALUE_KEYWORDS
            "INTERFACE_TUPLES"
    )
    set(OPTIONAL_MULTI_VALUE_KEYWORDS
            "INCLUDE_DIR_TUPLES"
            "MESSAGE_TUPLES"
            "DEPENDENCY_TUPLES"
    )

    cmake_parse_arguments(
            ARG "${FLAG_KEYWORDS}"
            "${REQUIRED_ONE_VALUE_KEYWORDS};${OPTIONAL_ONE_VALUE_KEYWORDS}"
            "${REQUIRED_MULTI_VALUE_KEYWORDS};${OPTIONAL_MULTI_VALUE_KEYWORDS}"
            ${ARGN}
    )

    if(ARG_UNPARSED_ARGUMENTS)
        message(FATAL_ERROR
                "rosidl_protozero_write_generator_arguments() called "
                "with unused arguments: ${ARG_UNPARSED_ARGUMENTS}"
        )
    endif()

    foreach(required_argument ${REQUIRED_ONE_VALUE_KEYWORDS})
        if(NOT ARG_${required_argument})
            message(FATAL_ERROR
                    "rosidl_protozero_write_generator_arguments() must "
                    "be invoked with the ${required_argument} argument"
            )
        endif()
    endforeach()

    foreach(required_argument ${REQUIRED_MULTI_VALUE_KEYWORDS})
        if(NOT ARG_${required_argument})
            message(FATAL_ERROR
                    "rosidl_protozero_write_generator_arguments() must "
                    "be invoked with the ${required_argument} argument"
            )
        endif()
    endforeach()

    set(arguments "{}")

    foreach (flag_argument ${FLAG_KEYWORDS})
        string(TOLOWER "${flag_argument}" key)

        if (ARG_${flag_argument})
            string(JSON arguments SET "${arguments}" "${key}" "true")
        else ()
            string(JSON arguments SET "${arguments}" "${key}" "false")
        endif ()
    endforeach ()

    foreach(one_value_argument ${REQUIRED_ONE_VALUE_KEYWORDS} ${OPTIONAL_ONE_VALUE_KEYWORDS})
        if (ARG_${one_value_argument})
            string(TOLOWER "${one_value_argument}" key)
            string(REPLACE "\\" "\\\\" value "${ARG_${one_value_argument}}")
            string(JSON arguments SET "${arguments}" "${key}" "\"${value}\"")
        endif ()
    endforeach ()

    foreach(multi_value_argument ${REQUIRED_MULTI_VALUE_KEYWORDS} ${OPTIONAL_MULTI_VALUE_KEYWORDS})
        if (ARG_${multi_value_argument})
            string(TOLOWER "${multi_value_argument}" key)
            string(JSON arguments SET "${arguments}" "${key}" "[]")

            list(LENGTH ARG_${multi_value_argument} length)
            math(EXPR length "${length} - 1")

            foreach(i RANGE ${length})
                list(GET ARG_${multi_value_argument} ${i} value)
                string(REPLACE "\\" "\\\\" value "${value}")
                string(JSON arguments SET "${arguments}" "${key}" ${i} "\"${value}\"")
            endforeach ()
        endif ()
    endforeach ()

    get_filename_component(output_path "${output_file}" PATH)
    file(MAKE_DIRECTORY "${output_path}")
    file(WRITE "${output_file}" "${arguments}")
endfunction()
