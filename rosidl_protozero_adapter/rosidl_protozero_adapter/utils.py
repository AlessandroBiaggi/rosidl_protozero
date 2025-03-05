from google.protobuf.descriptor_pb2 import FieldDescriptorProto, OneofDescriptorProto

from rosidl_protozero.options_pb2 import rosidl_field, rosidl_oneof


def has_field_flag(field: FieldDescriptorProto | OneofDescriptorProto) -> bool:
    if isinstance(field, FieldDescriptorProto):
        if field.HasField('oneof_index'):
            return False

        if field.HasField('options') and field.options.HasExtension(rosidl_field):
            opts = field.options.Extensions[rosidl_field]
            return opts.optional

        if field.HasField('label'):
            match field.label:
                case FieldDescriptorProto.Label.LABEL_REQUIRED:
                    return True
                case FieldDescriptorProto.Label.LABEL_OPTIONAL | FieldDescriptorProto.Label.LABEL_REPEATED:
                    return False
    elif isinstance(field, OneofDescriptorProto):
        if field.HasField('options') and field.options.HasExtension(rosidl_oneof):
            opts = field.options.Extensions[rosidl_oneof]
            return opts.optional

    return False

def has_decode_field_flag(field: FieldDescriptorProto | OneofDescriptorProto) -> bool:
    if has_field_flag(field):
        return False

    if (
            isinstance(field, FieldDescriptorProto)
            and
            field.HasField('label')
            and
            field.label == FieldDescriptorProto.Label.LABEL_REPEATED
    ):
            return False

    return True
