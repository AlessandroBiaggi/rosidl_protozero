@{
from google.protobuf.descriptor_pb2 import \
    DescriptorProto, \
    EnumDescriptorProto

from rosidl_protozero_adapter import deduce_idl_type
}@
@[if isinstance(message, DescriptorProto) and message.field]@
module @(struct_name)_Constants {
@[  for oneof_index, oneof_field in enumerate(message.oneof_decl)]@
@{      oneof_idl_type = deduce_idl_type(oneof_field, proto_types) }@
@[      for field in filter(lambda m, idx=oneof_index: m.HasField('oneof_index') and m.oneof_index == idx, message.field)]@
    const @(oneof_idl_type) @(naming_convention.oneof_value(message.name, oneof_field.name, field.name)) = @(field.number);
@[      end for]@

@[  end for]@
@[  for field in message.field]@
    const uint32 @(naming_convention.field_number(message.name, field.name)) = @(field.number);
@[  end for]@
};
@[elif isinstance(message, EnumDescriptorProto)]@
module @(struct_name)_Constants {
@{  enum_idl_type = deduce_idl_type(message, proto_types) }@
@[  for value in message.value]@
    const @(enum_idl_type) @(naming_convention.enum_value(message.name, value.name)) = @(value.number);
@[  end for]@
};
@[end if]@
