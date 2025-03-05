@{
import itertools

from google.protobuf.descriptor_pb2 import DescriptorProto, EnumDescriptorProto, FieldDescriptorProto

from rosidl_protozero_pycommon.utils import escape

from rosidl_protozero_adapter import deduce_idl_type
from rosidl_protozero_adapter.utils import has_field_flag

from rosidl_protozero.options_pb2 import rosidl_field

struct_name = naming_convention.struct(pkg_and_msg_name)
}@
struct @(struct_name) {
@[if isinstance(message, DescriptorProto)]@
@[  if message.field]@
@[      for field in filter(has_field_flag, itertools.chain(message.oneof_decl, message.field))]@
    boolean @(naming_convention.field_flag(pkg_and_msg_name, field.name));
@[      end for]@
@[      for curr_oneof_idx, oneof_field in enumerate(message.oneof_decl)]@
    @(deduce_idl_type(oneof_field, proto_types)) @(naming_convention.field(message.name, oneof_field.name));
@[          for field in filter(lambda m, idx=curr_oneof_idx: m.HasField('oneof_index') and idx == m.oneof_index, message.field)]@
@TEMPLATE(
    'struct__field.idl.em',
    field=field,
)
@[          end for]@
@[      end for]@
@[      for field in filter(lambda m: not m.HasField('oneof_index'), message.field)]@
@{          field_idl_type = deduce_idl_type(field, proto_types) }@
@TEMPLATE(
    'struct__field.idl.em',
    field=field,
)
@[      end for]@
@[  else]@
    uint8 structure_needs_at_least_one_member;
@[  end if]@
@[elif isinstance(message, EnumDescriptorProto)]@
@{  enum_idl_type = deduce_idl_type(message, proto_types) }@
    @(enum_idl_type) @(naming_convention.enum_field(message.name));
@[else]@
@{  raise RuntimeError(f"Message '{message.name}' is not supported") }@
@[end if]@
};@
