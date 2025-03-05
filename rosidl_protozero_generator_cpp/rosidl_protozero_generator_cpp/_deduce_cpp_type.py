from typing import Dict
from typing import Tuple

from google.protobuf.descriptor_pb2 import \
    FieldDescriptorProto, \
    EnumDescriptorProto, \
    OneofDescriptorProto
from rosidl_protozero_adapter import PROTOBUF_ROSIDL_CONVERTIBLE_TYPES
from rosidl_protozero.options_pb2 import \
    RosidlType, \
    RosidlSequenceSize, \
    rosidl_field, \
    rosidl_enum, \
    rosidl_oneof


ROSIDL_FIELD_TYPE = {
    RosidlType.ROSIDL_TYPE_BOOLEAN: 'bool',
    RosidlType.ROSIDL_TYPE_BYTE: 'std::byte',
    RosidlType.ROSIDL_TYPE_CHAR: 'char',
    RosidlType.ROSIDL_TYPE_FLOAT32: 'float',
    RosidlType.ROSIDL_TYPE_FLOAT64: 'double',
    RosidlType.ROSIDL_TYPE_INT8: 'std::int8_t',
    RosidlType.ROSIDL_TYPE_UINT8: 'std::uint8_t',
    RosidlType.ROSIDL_TYPE_INT16: 'std::int16_t',
    RosidlType.ROSIDL_TYPE_UINT16: 'std::uint16_t',
    RosidlType.ROSIDL_TYPE_INT32: 'std::int32_t',
    RosidlType.ROSIDL_TYPE_UINT32: 'std::uint32_t',
    RosidlType.ROSIDL_TYPE_INT64: 'std::int64_t',
    RosidlType.ROSIDL_TYPE_UINT64: 'std::uint64_t',
    RosidlType.ROSIDL_TYPE_STRING: 'std::string',
    RosidlType.ROSIDL_TYPE_WSTRING: 'std::wstring',
}

PROTOBUF_FIELD_TYPES_TO_PBF = {
    # FieldDescriptorProto.Type -> (field_pbf_wire_type, field_pbf_type, field_pbf_getter, field_pbf_adder, packed_pbf_field)
    FieldDescriptorProto.TYPE_DOUBLE: ('fixed64', 'double', 'get_double', 'add_double', 'packed_field_double'),
    FieldDescriptorProto.TYPE_FLOAT: ('fixed32', 'float', 'get_float', 'add_float', 'packed_field_float'),
    FieldDescriptorProto.TYPE_INT32: ('varint', 'std::int32_t', 'get_int32', 'add_int32', 'packed_field_int32'),
    FieldDescriptorProto.TYPE_INT64: ('varint', 'std::int64_t', 'get_int64', 'add_int64', 'packed_field_int64'),
    FieldDescriptorProto.TYPE_UINT32: ('varint', 'std::uint32_t', 'get_uint32', 'add_uint32', 'packed_field_uint32'),
    FieldDescriptorProto.TYPE_UINT64: ('varint', 'std::uint64_t', 'get_uint64', 'add_uint64', 'packed_field_uint64'),
    FieldDescriptorProto.TYPE_SINT32: ('varint', 'std::int32_t', 'get_sint32', 'add_sint32', 'packed_field_sint32'),
    FieldDescriptorProto.TYPE_SINT64: ('varint', 'std::int64_t', 'get_sint64', 'add_sint64', 'packed_field_sint64'),
    FieldDescriptorProto.TYPE_FIXED32: ('fixed32', 'std::uint32_t', 'get_fixed32', 'add_fixed32', 'packed_field_fixed32'),
    FieldDescriptorProto.TYPE_FIXED64: ('fixed64', 'std::uint64_t', 'get_fixed64', 'add_fixed64', 'packed_field_fixed64'),
    FieldDescriptorProto.TYPE_SFIXED32: ('fixed32', 'std::int32_t', 'get_sfixed32', 'add_sfixed32', 'packed_field_sfixed32'),
    FieldDescriptorProto.TYPE_SFIXED64: ('fixed64', 'std::int64_t', 'get_sfixed64', 'add_sfixed64', 'packed_field_sfixed64'),
    FieldDescriptorProto.TYPE_BOOL: ('varint', 'bool', 'get_bool', 'add_bool', 'packed_field_bool'),
    FieldDescriptorProto.TYPE_STRING: ('length_delimited', '', 'get_view', 'add_bytes', ''),
    FieldDescriptorProto.TYPE_BYTES: ('length_delimited', 'char[]', 'get_view', 'add_bytes', ''),
    FieldDescriptorProto.TYPE_ENUM: ('varint', 'std::int32_t', 'get_enum', 'add_enum', 'packed_field_enum'),
    FieldDescriptorProto.TYPE_MESSAGE: ('length_delimited', '', 'get_message', '', ''),
}

def deduce_cpp_type(
        field: FieldDescriptorProto | EnumDescriptorProto | OneofDescriptorProto,
        proto_types: Dict[Tuple[str, ...], Tuple[str, ...]],
) -> Tuple[str, str, str, str, str, str, str]:
    if isinstance(field, FieldDescriptorProto):
        if field.type in PROTOBUF_FIELD_TYPES_TO_PBF:
            field_data = PROTOBUF_FIELD_TYPES_TO_PBF[field.type]
            field_cpp_package = ''
            field_cpp_type = field_data[1]
        else:
            raise RuntimeError(f"Field {field.name} of type {field.type} cannot be converted to C++")

        if field.type in (FieldDescriptorProto.TYPE_MESSAGE, FieldDescriptorProto.TYPE_ENUM):
            _, *type_name = field.type_name.split('.')
            type_name = tuple(type_name)

            if type_name not in proto_types:
                import pprint
                raise RuntimeError(f"Unknown message '{field.type_name}'\n{pprint.pformat(proto_types)}")

            field_cpp_package = proto_types[type_name][0]
            field_cpp_type = '::'.join(proto_types[type_name])

        if field.HasField('options') and field.options.HasExtension(rosidl_field):
            opts = field.options.Extensions[rosidl_field]

            if opts.HasField('type'):
                if not any(field.type in proto_types and opts.type in rosidl_types
                           for proto_types, rosidl_types in PROTOBUF_ROSIDL_CONVERTIBLE_TYPES.items()):
                    raise RuntimeError(
                        f"Field {field.name} of type {field.type} cannot be converted to C++ type {opts.type}")
                field_cpp_type = ROSIDL_FIELD_TYPE[opts.type]
    elif isinstance(field, EnumDescriptorProto):
        field_data = PROTOBUF_FIELD_TYPES_TO_PBF[FieldDescriptorProto.TYPE_ENUM]
        field_cpp_package = ''
        field_cpp_type = field_data[1]

        if field.HasField('options') and field.options.HasExtension(rosidl_enum):
            opts = field.options.Extensions[rosidl_enum]

            if opts.HasField('type'):
                if not any(FieldDescriptorProto.TYPE_ENUM in proto_types and opts.type in rosidl_types
                           for proto_types, rosidl_types in PROTOBUF_ROSIDL_CONVERTIBLE_TYPES.items()):
                    raise RuntimeError(f"Enum {field.name} cannot be converted to IDL type {opts.type}")
                field_cpp_type = ROSIDL_FIELD_TYPE[opts.type]

            if opts.HasField('sequence_capacity') or opts.HasField('sequence_size'):
                raise RuntimeError(f"Oneof {field.name} cannot have sequence capacity or size")
    elif isinstance(field, OneofDescriptorProto):
        field_data = PROTOBUF_FIELD_TYPES_TO_PBF[FieldDescriptorProto.TYPE_INT32]
        field_cpp_package = ''
        field_cpp_type = field_data[1]

        if field.HasField('options') and field.options.HasExtension(rosidl_oneof):
            opts = field.options.Extensions[rosidl_oneof]

            if opts.HasField('type'):
                if not any(FieldDescriptorProto.TYPE_ENUM in proto_types and opts.type in rosidl_types
                           for proto_types, rosidl_types in PROTOBUF_ROSIDL_CONVERTIBLE_TYPES.items()):
                    raise RuntimeError(f"Oneof {field.name} cannot be converted to IDL type {opts.type}")
                field_cpp_type = ROSIDL_FIELD_TYPE[opts.type]

            if opts.HasField('sequence_capacity') or opts.HasField('sequence_size'):
                raise RuntimeError(f"Oneof {field.name} cannot have sequence capacity or size")
    else:
        raise RuntimeError(f"Field {field.name} of type {type(field)} cannot be converted to C++")

    return field_cpp_package, field_cpp_type, *field_data
