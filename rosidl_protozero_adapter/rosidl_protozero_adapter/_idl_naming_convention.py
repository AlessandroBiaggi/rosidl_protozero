from typing import Tuple

from rosidl_protozero_pycommon import \
    NamingConvention, \
    to_pascal_case, \
    to_snake_case


class IdlNamingConvention(NamingConvention):
    def idl_name(self, message_name: str | Tuple[str, ...]) -> str:
        return self.struct(message_name)

    def struct(self, message_name: str | Tuple[str, ...], *argv: str) -> str:
        if isinstance(message_name, str):
            message_name = (message_name,)

        return ''.join(map(to_pascal_case, [
            *message_name,
            *argv,
        ]))

    def stamped_struct(self, message_name: str | Tuple[str, ...]) -> str:
        return self.struct(message_name, 'stamped')

    def field(self, _message_name: str | Tuple[str, ...], field_name: str) -> str:
        return to_snake_case(field_name)

    def field_number(self, _message_name: str | Tuple[str, ...], field_name: str) -> str:
        return f"{self.field(_message_name, field_name).upper()}_NUMBER"

    def field_flag(self, _message_name: str | Tuple[str, ...], field_name: str) -> str:
        return f"has_{self.field(_message_name, field_name)}"

    def enum_field(self, _message_name: str | Tuple[str, ...]) -> str:
        return 'value'

    def enum_value(self, _enum_name: str | Tuple[str, ...], value_name: str) -> str:
        return to_snake_case(value_name).upper()

    def oneof_value(self, _message_name: str | Tuple[str, ...], oneof_field_name: str, field_name: str) -> str:
        return '__'.join(map(to_snake_case, [oneof_field_name, 'oneof', field_name])).upper()

    def header_field_name(self, _message_name: str | Tuple[str, ...]) -> str:
        return 'header'

    def struct_field_name(self, message_name: str | Tuple[str, ...]) -> str:
        return to_snake_case(message_name)
