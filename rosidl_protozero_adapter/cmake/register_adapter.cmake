macro(rosidl_protozero_adapter_c_extras BIN GENERATOR_FILES TEMPLATE_DIR)
    normalize_path(BIN "${BIN}")
    set(rosidl_protozero_adapter_BIN "${BIN}")

    normalize_path(GENERATOR_FILES "${GENERATOR_FILES}")
    set(rosidl_protozero_adapter_GENERATOR_FILES "${GENERATOR_FILES}")

    normalize_path(TEMPLATE_DIR "${TEMPLATE_DIR}")
    set(rosidl_protozero_adapter_TEMPLATE_DIR "${TEMPLATE_DIR}")
endmacro()
