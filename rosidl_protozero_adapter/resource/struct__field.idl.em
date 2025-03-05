@{
from google.protobuf.descriptor_pb2 import FieldDescriptorProto

from rosidl_protozero.options_pb2 import \
    RosidlSequenceSize, \
    rosidl_field

from rosidl_protozero_adapter import deduce_idl_type

field_idl_type = deduce_idl_type(field, proto_types)
field_idl_name = naming_convention.field(message.name, field.name)
}@
@[if not field.HasField('label') or field.label is not FieldDescriptorProto.Label.LABEL_REPEATED]@
    @(field_idl_type) @(field_idl_name);
@[elif not field.options.HasExtension(rosidl_field)]@
    sequence<@(field_idl_type)> @(field_idl_name);
@[else]@
@{  field_opts = field.options.Extensions[rosidl_field] }@
@[  if field_opts.sequence_size is RosidlSequenceSize.ROSIDL_SEQUENCE_DYNAMIC_SIZE]@
    sequence<@(field_idl_type)> @(field_idl_name);
@[  elif field_opts.sequence_size is RosidlSequenceSize.ROSIDL_SEQUENCE_FIXED_SIZE]@
@{
assert field_opts.HasField('sequence_capacity') and field_opts.sequence_capacity > 0, \
    f"Repeated field with fixed size '{field.name}' " \
    f"in message '{message.name}' must have a sequence capacity greater that zero"
}@
    @(field_idl_type) @(field_idl_name)[@(field_opts.sequence_capacity)];
@[  elif field_opts.sequence_size is RosidlSequenceSize.ROSIDL_SEQUENCE_BOUNDED_SIZE]@
@{
assert field_opts.HasField('sequence_capacity') and field_opts.sequence_capacity > 0, \
    f"Repeated field with bounded size '{field.name}' " \
    f"in message '{message.name}' must have a sequence capacity greater that zero"
}@
    sequence<@(field_idl_type), @(field_opts.sequence_capacity)> @(field_idl_name);
@[  else]@
@{      raise RuntimeError(f"Field '{field.name}' in message '{message.name}' has invalid sequence size") }@
@[  end if]@
@[end if]@
