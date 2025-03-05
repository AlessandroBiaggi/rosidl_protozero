@{
from google.protobuf.descriptor_pb2 import DescriptorProto, EnumDescriptorProto, FieldDescriptorProto

header_guard = naming_convention.header_guard(package_name, 'protozero', 'detail', *pkg_and_msg_name, 'tags')

namespace = naming_convention.namespace()
struct_name = naming_convention.struct(pkg_and_msg_name)
decode_decl_name = naming_convention.decode_decl()
}@
#ifndef @(header_guard)
#define @(header_guard)

#include <memory>

#include <protozero/types.hpp>

#include <@(package_name)/@(naming_convention.struct_header_path(pkg_and_msg_name))>
#include <@(package_name)/@(naming_convention.visibility_control_header_path())>

namespace @(package_name)::@(namespace) {

    @(naming_convention.visibility_control_public())
    enum class @(struct_name) : protozero::pbf_tag_type {
@[if isinstance(message, DescriptorProto)]@
@[  for field in message.field]@
@{      field_name = naming_convention.field(pkg_and_msg_name, field.name) }@
@{      field_number = naming_convention.field_number(pkg_and_msg_name, field.name) }@
        @(field_name) = @(package_name)::msg::@(struct_name)::@(field_number),
@[  end for]@
@[elif isinstance(message, EnumDescriptorProto)]@
@[  for value in message.value]@
@{      value_name = naming_convention.enum_value(pkg_and_msg_name, value.name) }@
        @(value_name) = @(package_name)::msg::@(struct_name)::@(value_name),
@[  end for]@
@[else]@
@{  raise RuntimeError(f"Unsupported message type '{message}'")}@
@[end if]@
    };

} // namespace @(package_name)::@(namespace)

#endif // @(header_guard)
