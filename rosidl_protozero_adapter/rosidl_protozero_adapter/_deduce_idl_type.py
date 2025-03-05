from typing import Dict
from typing import Tuple

from google.protobuf.descriptor_pb2 import \
    FieldDescriptorProto, \
    EnumDescriptorProto, \
    OneofDescriptorProto
from rosidl_protozero.options_pb2 import \
    RosidlType, \
    RosidlSequenceSize, \
    rosidl_field, \
    rosidl_enum, \
    rosidl_oneof

PROTOBUF_FIELD_TYPES_TO_IDL = {
    FieldDescriptorProto.TYPE_DOUBLE: 'double',
    FieldDescriptorProto.TYPE_FLOAT: 'float',
    FieldDescriptorProto.TYPE_INT32: 'int32',
    FieldDescriptorProto.TYPE_INT64: 'int64',
    FieldDescriptorProto.TYPE_UINT32: 'uint32',
    FieldDescriptorProto.TYPE_UINT64: 'uint64',
    FieldDescriptorProto.TYPE_SINT32: 'int32',
    FieldDescriptorProto.TYPE_SINT64: 'int64',
    FieldDescriptorProto.TYPE_FIXED32: 'uint32',
    FieldDescriptorProto.TYPE_FIXED64: 'uint64',
    FieldDescriptorProto.TYPE_SFIXED32: 'int32',
    FieldDescriptorProto.TYPE_SFIXED64: 'int64',
    FieldDescriptorProto.TYPE_BOOL: 'boolean',
    FieldDescriptorProto.TYPE_STRING: 'string',
    FieldDescriptorProto.TYPE_BYTES: 'std_msgs::msg::ByteMultiArray',
}

ROSIDL_FIELD_TYPE = {
    RosidlType.ROSIDL_TYPE_BOOLEAN: 'boolean',
    RosidlType.ROSIDL_TYPE_BYTE: 'octet',
    RosidlType.ROSIDL_TYPE_CHAR: 'char',
    RosidlType.ROSIDL_TYPE_FLOAT32: 'float32',
    RosidlType.ROSIDL_TYPE_FLOAT64: 'float64',
    RosidlType.ROSIDL_TYPE_INT8: 'int8',
    RosidlType.ROSIDL_TYPE_UINT8: 'uint8',
    RosidlType.ROSIDL_TYPE_INT16: 'int16',
    RosidlType.ROSIDL_TYPE_UINT16: 'uint16',
    RosidlType.ROSIDL_TYPE_INT32: 'int32',
    RosidlType.ROSIDL_TYPE_UINT32: 'uint32',
    RosidlType.ROSIDL_TYPE_INT64: 'int64',
    RosidlType.ROSIDL_TYPE_UINT64: 'uint64',
    RosidlType.ROSIDL_TYPE_STRING: 'string',
    RosidlType.ROSIDL_TYPE_WSTRING: 'wstring',
}

PROTOBUF_ROSIDL_CONVERTIBLE_TYPES = {
    (FieldDescriptorProto.TYPE_DOUBLE,
     FieldDescriptorProto.TYPE_FLOAT):
        (RosidlType.ROSIDL_TYPE_FLOAT32,
         RosidlType.ROSIDL_TYPE_FLOAT64),
    (FieldDescriptorProto.TYPE_INT32,
     FieldDescriptorProto.TYPE_INT64,
     FieldDescriptorProto.TYPE_SINT32,
     FieldDescriptorProto.TYPE_SINT64,
     FieldDescriptorProto.TYPE_SFIXED32,
     FieldDescriptorProto.TYPE_SFIXED64):
        (RosidlType.ROSIDL_TYPE_INT8,
         RosidlType.ROSIDL_TYPE_INT16,
         RosidlType.ROSIDL_TYPE_INT32,
         RosidlType.ROSIDL_TYPE_INT64),
    (FieldDescriptorProto.TYPE_UINT32,
     FieldDescriptorProto.TYPE_UINT64,
     FieldDescriptorProto.TYPE_FIXED32,
     FieldDescriptorProto.TYPE_FIXED64):
        (RosidlType.ROSIDL_TYPE_UINT8,
         RosidlType.ROSIDL_TYPE_UINT16,
         RosidlType.ROSIDL_TYPE_UINT32,
         RosidlType.ROSIDL_TYPE_UINT64),
    (FieldDescriptorProto.TYPE_BOOL,):
        (RosidlType.ROSIDL_TYPE_BOOLEAN,),
    (FieldDescriptorProto.TYPE_STRING,):
        (RosidlType.ROSIDL_TYPE_STRING,
         RosidlType.ROSIDL_TYPE_WSTRING),
    (FieldDescriptorProto.TYPE_ENUM,):
        (RosidlType.ROSIDL_TYPE_INT8,
         RosidlType.ROSIDL_TYPE_INT16,
         RosidlType.ROSIDL_TYPE_INT32,
         RosidlType.ROSIDL_TYPE_INT64,
         RosidlType.ROSIDL_TYPE_UINT8,
         RosidlType.ROSIDL_TYPE_UINT16,
         RosidlType.ROSIDL_TYPE_UINT32,
         RosidlType.ROSIDL_TYPE_UINT64),
}

PROTOBUF_WELL_KNOWN_TYPES_TO_IDL = {
    ("google", "protobuf", "Empty"): ("std_msgs", "msg", "Empty"),
    ("google", "protobuf", "Duration"): ("builtin_interfaces", "msg", "Duration"),
    ("google", "protobuf", "Timestamp"): ("builtin_interfaces", "msg", "Time"),
    # TODO add more well-known types
}


def deduce_idl_type(
        field: FieldDescriptorProto | EnumDescriptorProto | OneofDescriptorProto,
        proto_types: Dict[Tuple[str, ...], Tuple[str, ...]],
) -> str:
    if isinstance(field, FieldDescriptorProto):
        if field.type in PROTOBUF_FIELD_TYPES_TO_IDL:
            t = PROTOBUF_FIELD_TYPES_TO_IDL[field.type]
        elif field.type in (FieldDescriptorProto.TYPE_MESSAGE, FieldDescriptorProto.TYPE_ENUM):
            _, *type_name = field.type_name.split('.')
            type_name = tuple(type_name)

            if type_name not in proto_types:
                raise RuntimeError(f"Unknown message '{field.type_name}'")

            t = '::'.join(proto_types[type_name])
        else:
            raise RuntimeError(f"Field {field.name} of type {field.type} cannot be converted to IDL")

        if field.HasField('options') and field.options.HasExtension(rosidl_field):
            opts = field.options.Extensions[rosidl_field]

            if opts.HasField('type'):
                if not any(field.type in proto_types and opts.type in rosidl_types
                           for proto_types, rosidl_types in PROTOBUF_ROSIDL_CONVERTIBLE_TYPES.items()):
                    raise RuntimeError(
                        f"Field {field.name} of type {field.type} cannot be converted to IDL type {opts.type}")
                t = ROSIDL_FIELD_TYPE[opts.type]
    elif isinstance(field, EnumDescriptorProto):
        t = PROTOBUF_FIELD_TYPES_TO_IDL[FieldDescriptorProto.TYPE_INT32]

        if field.HasField('options') and field.options.HasExtension(rosidl_enum):
            opts = field.options.Extensions[rosidl_enum]

            if opts.HasField('type'):
                if not any(FieldDescriptorProto.TYPE_ENUM in proto_types and opts.type in rosidl_types
                           for proto_types, rosidl_types in PROTOBUF_ROSIDL_CONVERTIBLE_TYPES.items()):
                    raise RuntimeError(f"Enum {field.name} cannot be converted to IDL type {opts.type}")
                t = ROSIDL_FIELD_TYPE[opts.type]

            if opts.HasField('sequence_capacity') or opts.HasField('sequence_size'):
                raise RuntimeError(f"Oneof {field.name} cannot have sequence capacity or size")
    elif isinstance(field, OneofDescriptorProto):
        t = PROTOBUF_FIELD_TYPES_TO_IDL[FieldDescriptorProto.TYPE_INT32]

        if field.HasField('options') and field.options.HasExtension(rosidl_oneof):
            opts = field.options.Extensions[rosidl_oneof]

            if opts.HasField('type'):
                if not any(FieldDescriptorProto.TYPE_ENUM in proto_types and opts.type in rosidl_types
                           for proto_types, rosidl_types in PROTOBUF_ROSIDL_CONVERTIBLE_TYPES.items()):
                    raise RuntimeError(f"Oneof {field.name} cannot be converted to IDL type {opts.type}")
                t = ROSIDL_FIELD_TYPE[opts.type]

            if opts.HasField('sequence_capacity') or opts.HasField('sequence_size'):
                raise RuntimeError(f"Oneof {field.name} cannot have sequence capacity or size")
    else:
        raise RuntimeError(f"Field {field.name} of type {type(field)} cannot be converted to IDL")

    return t
