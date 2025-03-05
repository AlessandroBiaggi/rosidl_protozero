from typing import Tuple

import re
import pathlib

from rosidl_protozero_pycommon import \
    NamingConvention, \
    to_snake_case, \
    to_pascal_case

from rosidl_protozero_adapter import IdlNamingConvention


class CppNamingConvention(NamingConvention):
    def __init__(
            self,
            package_name: str
    ):
        self._package_name = package_name

        self._idl_naming_convention = IdlNamingConvention()
        self._namespace = ('pbf', )

    def namespace(self) -> str:
        return '::'.join(self._namespace)

    def struct(self, message_name: str | Tuple[str, ...]) -> str:
        return self._idl_naming_convention.struct(message_name)

    def stamped_struct(self, message_name: str | Tuple[str, ...]) -> str:
        return self._idl_naming_convention.stamped_struct(message_name)

    def struct_header_name(self, message_name: str | Tuple[str, ...]) -> str:
        if not isinstance(message_name, str):
            message_name = self.struct(message_name)

        # See rosidl_cmake/cmake/string_camel_case_to_lower_case_underscore.cmake
        message_name = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', message_name)
        message_name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', message_name)
        return message_name.lower()

    def struct_header_path(self, message_name: str | Tuple[str, ...]) -> pathlib.Path:
        return pathlib.Path('msg', self.struct_header_name(message_name)).with_suffix('.hpp')

    def struct_interface_header_path(self, message_name: str | Tuple[str, ...]) -> pathlib.Path:
        return pathlib.Path(*self._namespace, f"{self.struct_header_name(message_name)}").with_suffix('.hpp')

    def struct_tags_header_path(self, message_name: str | Tuple[str, ...]) -> pathlib.Path:
        return pathlib.Path(*self._namespace, 'detail', f"{self.struct_header_name(message_name)}__tags").with_suffix('.hpp')

    def struct_encode_header_path(self, message_name: str | Tuple[str, ...]) -> pathlib.Path:
        return pathlib.Path(*self._namespace, 'detail', f"{self.struct_header_name(message_name)}__encode").with_suffix('.hpp')

    def struct_decode_header_path(self, message_name: str | Tuple[str, ...]) -> pathlib.Path:
        return pathlib.Path(*self._namespace, 'detail', f"{self.struct_header_name(message_name)}__decode").with_suffix('.hpp')

    def visibility_control_header_path(self) -> pathlib.Path:
        return pathlib.Path('rosidl_protozero_generator_cpp__visibility_control').with_suffix('.hpp')

    def header_field_name(self, message_name: str | Tuple[str, ...]) -> str:
        return self._idl_naming_convention.header_field_name(message_name)

    def struct_field_name(self, message_name: str | Tuple[str, ...]) -> str:
        return self._idl_naming_convention.struct_field_name(message_name)

    def field(self, message_name: str | Tuple[str, ...], field_name: str) -> str:
        return self._idl_naming_convention.field(message_name, field_name)

    def field_number(self, message_name: str | Tuple[str, ...], field_name: str) -> str:
        return self._idl_naming_convention.field_number(message_name, field_name)

    def field_flag(self, message_name: str | Tuple[str, ...], field_name: str) -> str:
        return self._idl_naming_convention.field_flag(message_name, field_name)

    def enum_value(self, message_name: str | Tuple[str, ...], enum_value_name: str) -> str:
        return self._idl_naming_convention.enum_value(message_name, enum_value_name)

    def enum_field(self, _message_name: str | Tuple[str, ...]) -> str:
        return 'value'

    def _macro(self, *argv: str) -> str:
        return '__'.join([
            *self._namespace,
            *argv,
        ]).upper()

    def header_guard(self, *argv: str) -> str:
        return self._macro(*map(to_snake_case, argv), 'HPP')

    def visibility_control_public(self) -> str:
        return f"rosidl_protozero_generator_cpp_PUBLIC_{self._package_name}"

    def visibility_control_export(self) -> str:
        return f"rosidl_protozero_generator_cpp_EXPORT_{self._package_name}"

    def visibility_control_import(self) -> str:
        return f"rosidl_protozero_generator_cpp_IMPORT_{self._package_name}"

    def encode_decl(self) -> str:
        return 'encode'

    def decode_decl(self) -> str:
        return 'decode'

    def validate_decl(self) -> str:
        return 'validate'
