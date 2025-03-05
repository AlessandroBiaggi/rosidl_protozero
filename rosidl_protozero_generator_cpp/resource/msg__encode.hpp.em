@{
from google.protobuf.descriptor_pb2 import DescriptorProto, EnumDescriptorProto, FieldDescriptorProto

from rosidl_protozero_adapter.utils import has_field_flag

from rosidl_protozero_generator_cpp import deduce_cpp_type

header_guard = naming_convention.header_guard(package_name, 'protozero', 'detail', *pkg_and_msg_name, 'encode')

namespace = naming_convention.namespace()
struct_name = naming_convention.struct(pkg_and_msg_name)
encode_decl_name = naming_convention.encode_decl()

includes = set()
if isinstance(message, DescriptorProto):
    for field in filter(lambda f, T=FieldDescriptorProto.Type: f.type in (T.TYPE_MESSAGE, T.TYPE_ENUM), message.field):
        field_cpp_package, *_ = deduce_cpp_type(field, proto_types)
        _, *field_type_name = field.type_name.split('.')
        includes.add((field_cpp_package, tuple(field_type_name)))
}@
#ifndef @(header_guard)
#define @(header_guard)

#include <cstddef>
#include <cstdint>
#include <limits>
#include <type_traits>

#include <protozero/basic_pbf_builder.hpp>
#include <protozero/types.hpp>

#include <@(package_name)/@(naming_convention.struct_header_path(pkg_and_msg_name))>
#include <@(package_name)/@(naming_convention.struct_tags_header_path(pkg_and_msg_name))>
#include <@(package_name)/@(naming_convention.visibility_control_header_path())>

@[for field_cpp_package, field_type_name in sorted(includes)]@
#include <@(field_cpp_package)/@(naming_convention.struct_encode_header_path(field_type_name))>
@[end for]@

namespace @(package_name)::@(namespace) {

    template<typename BufferT, typename AllocatorT>
    @(naming_convention.visibility_control_public())
    bool @(encode_decl_name)(
             const @(package_name)::msg::@(struct_name)_<AllocatorT> &src,
             protozero::basic_pbf_builder<BufferT, @(struct_name)> dst
    ) noexcept {
        bool ok = true;
        try {
@[if isinstance(message, DescriptorProto)]@
@[  for oneof_idx, oneof_field in enumerate(message.oneof_decl)]@
            @(has_field_flag(oneof_field) ? f"if (src.{naming_convention.field_flag(pkg_and_msg_name, oneof_field.name)}) "){
@{      oneof_field_name = naming_convention.field(pkg_and_msg_name, oneof_field.name) }@
                switch (src.@(naming_convention.field(pkg_and_msg_name, oneof_field_name))) {
@[      for field in filter(lambda f, idx=oneof_idx: f.HasField('oneof_index') and f.oneof_index == idx, message.field)]@
@{          field_name = naming_convention.field(pkg_and_msg_name, field.name) }@
@{          field_cpp_package, field_cpp_type, _, field_pbf_type, _, field_pbf_adder, _ = deduce_cpp_type(field, proto_types) }@
                    case @(struct_name)::@(field_name): {
@[          if field.type == FieldDescriptorProto.Type.TYPE_MESSAGE]@
@{              field_pkg_and_msg_name = naming_convention.struct(tuple(field.type_name.split('.')[1:])) }@
                        ok &= @(field_cpp_package)::@(namespace)::@(encode_decl_name)(src.@(field_name), protozero::basic_pbf_builder<BufferT, @(field_pkg_and_msg_name)>{dst, @(struct_name)::@(field_name)});
@[          elif field.type == FieldDescriptorProto.Type.TYPE_BYTES]@
                        dst.@(field_pbf_adder)(@(struct_name)::@(field_name), static_cast<@(field_pbf_type)>(src.@(field_name).data.data()), src.@(field_name).data.size());
@[          elif field.type == FieldDescriptorProto.Type.TYPE_STRING]@
                        dst.@(field_pbf_adder)(@(struct_name)::@(field_name), src.@(field_name));
@[          else]@
@{              field_needs_cast = False }@
@[              if field.type != FieldDescriptorProto.Type.TYPE_ENUM]@
@[                  if field_cpp_type != field_pbf_type]@
@{                      field_needs_cast = True }@
                        using value_type = std::common_type_t<@(field_cpp_type), @(field_pbf_type)>;
                        constexpr auto min = static_cast<value_type>(std::numeric_limits<@(field_pbf_type)>::min());
                        constexpr auto max = static_cast<value_type>(std::numeric_limits<@(field_pbf_type)>::max());
@[                  end if]@
@[              else]@
@{                  enum_field_type = tuple(field.type_name.split('.')[1:]) }@
@{                  _, enum_cpp_type, _, enum_pbf_type, _, _, _ = deduce_cpp_type(all_messages[enum_field_type], proto_types) }@
@[                  if enum_cpp_type != enum_pbf_type]@
@{                      field_needs_cast = True }@
                        using value_type = std::common_type_t<@(enum_cpp_type), @(enum_pbf_type)>;
                        constexpr auto min = static_cast<value_type>(std::numeric_limits<@(enum_pbf_type)>::min());
                        constexpr auto max = static_cast<value_type>(std::numeric_limits<@(enum_pbf_type)>::max());
@[                  end if]@
@[              end if]@
@[              if field_needs_cast]@
                        const auto value = static_cast<value_type>(src.@(field_name));
                        if (min <= value && value <= max) {
@[                  if field.type != FieldDescriptorProto.Type.TYPE_ENUM]@
                            dst.@(field_pbf_adder)(@(struct_name)::@(field_name), static_cast<@(field_pbf_type)>(src.@(field_name)));
@[                  else]@
@{                      enum_pkg_and_msg_name = proto_types[tuple(field.type_name.split('.')[1:])] }@
@{                      enum_field_name = naming_convention.enum_field(enum_pkg_and_msg_name) }@
                            dst.@(field_pbf_adder)(@(struct_name)::@(field_name), static_cast<@(enum_pbf_type)>(src.@(field_name).@(enum_field_name)));
@[                  end if]@
                        } else {
                            ok = false;
                        }
@[              else]@
@[                  if field.type != FieldDescriptorProto.Type.TYPE_ENUM]@
                        dst.@(field_pbf_adder)(@(struct_name)::@(field_name), src.@(field_name));
@[                  else]@
@{                      enum_pkg_and_msg_name = proto_types[tuple(field.type_name.split('.')[1:])] }@
@{                      enum_field_name = naming_convention.enum_field(enum_pkg_and_msg_name) }@
                        dst.@(field_pbf_adder)(@(struct_name)::@(field_name), src.@(field_name).@(enum_field_name));
@[                  end if]@
@[              end if]@
@[          end if]@
                        break;
                    }
@[      end for]@
                    default: {
                        ok = false;
                        break;
                    }
                }
            }
@[  end for]@
@[  for field in filter(lambda f: not f.HasField('oneof_index'), message.field)]@
@{      field_name = naming_convention.field(pkg_and_msg_name, field.name) }@
@{      field_cpp_package, field_cpp_type, _, field_pbf_type, _, field_pbf_adder, packed_pbf_field = deduce_cpp_type(field, proto_types) }@
            @(has_field_flag(field) ? f"if (src.{naming_convention.field_flag(pkg_and_msg_name, field.name)}) "){
@{      field_needs_cast = False }@
@[      if field.type not in (FieldDescriptorProto.Type.TYPE_MESSAGE, FieldDescriptorProto.Type.TYPE_ENUM, FieldDescriptorProto.Type.TYPE_BYTES, FieldDescriptorProto.Type.TYPE_STRING)]@
@[          if field_cpp_type != field_pbf_type]@
@{              field_needs_cast = True }@
                using value_type = std::common_type_t<@(field_cpp_type), @(field_pbf_type)>;
                constexpr auto min = static_cast<value_type>(std::numeric_limits<@(field_pbf_type)>::min());
                constexpr auto max = static_cast<value_type>(std::numeric_limits<@(field_pbf_type)>::max());
@[          end if]@
@[      elif field.type == FieldDescriptorProto.Type.TYPE_ENUM]@
@{          enum_field_type = tuple(field.type_name.split('.')[1:]) }@
@{          _, enum_cpp_type, _, enum_pbf_type, _, _, _ = deduce_cpp_type(all_messages[enum_field_type], proto_types) }@
@[          if enum_cpp_type != enum_pbf_type]@
@{              field_needs_cast = True }@
                using value_type = std::common_type_t<@(enum_cpp_type), @(enum_pbf_type)>;
                constexpr auto min = static_cast<value_type>(std::numeric_limits<@(enum_pbf_type)>::min());
                constexpr auto max = static_cast<value_type>(std::numeric_limits<@(enum_pbf_type)>::max());
@[          end if]@
@[      end if]@
@[      if field.label == FieldDescriptorProto.Label.LABEL_REPEATED]@
@[          if field.HasField('options') and field.options.packed]@
@{              assert field.type != FieldDescriptorProto.Type.TYPE_MESSAGE, f"Field '{field.name}' is message or enum"}@
                {
                    bool field_ok = true;
                    protozero::@(packed_pbf_field) field{dst, @(struct_name)::@(field_name), src.@(field_name).size()};
                    for (auto it = src.@(field_name).cbegin(); field_ok && it != src.@(field_name).cend(); ++it) {
@[              if field_needs_cast]@
                        const auto value = static_cast<value_type>(*it);
                        if (min <= value && value <= max) {
@[                  if field.type != FieldDescriptorProto.Type.TYPE_ENUM]@
                            field.add_element(static_cast<@(field_pbf_type)>(*it));
@[                  else]@
@{                      enum_pkg_and_msg_name = proto_types[tuple(field.type_name.split('.')[1:])] }@
@{                      enum_field_name = naming_convention.enum_field(enum_pkg_and_msg_name) }@
                            field.add_element(static_cast<@(enum_pbf_type)>(it->@(enum_field_name)));
@[                  end if]@
                        } else {
                            field_ok = false;
                        }
@[              else]@
@[                  if field.type != FieldDescriptorProto.Type.TYPE_ENUM]@
                        field.add_element(*it);
@[                  else]@
@{                      enum_pkg_and_msg_name = proto_types[tuple(field.type_name.split('.')[1:])] }@
@{                      enum_field_name = naming_convention.enum_field(enum_pkg_and_msg_name) }@
                        field.add_element(it->@(enum_field_name));
@[                  end if]@
@[              end if]@
                    }
                    ok &= field_ok;
                }
@[          else]@
                bool field_ok = true;
                for (auto it = src.@(field_name).cbegin(); field_ok && it != src.@(field_name).cend(); ++it) {
@[              if field.type == FieldDescriptorProto.Type.TYPE_MESSAGE]@
@{                  field_pkg_and_msg_name = naming_convention.struct(tuple(field.type_name.split('.')[1:])) }@
                    field_ok &= @(field_cpp_package)::@(namespace)::@(encode_decl_name)(*it, protozero::basic_pbf_builder<BufferT, @(field_pkg_and_msg_name)>{dst, @(struct_name)::@(field_name)});
@[              elif field.type == FieldDescriptorProto.Type.TYPE_BYTES]@
                    dst.@(field_pbf_adder)(@(struct_name)::@(field_name), static_cast<@(field_pbf_type)>(it->data.data()), it->data.size());
@[              elif field.type == FieldDescriptorProto.Type.TYPE_STRING]@
                    dst.@(field_pbf_adder)(@(struct_name)::@(field_name), *it);
@[              else]@
@[                  if field_needs_cast]@
                    const auto value = static_cast<value_type>(*it);
                    if (min <= value && value <= max) {
@[                      if field.type != FieldDescriptorProto.Type.TYPE_ENUM]@
                        dst.@(field_pbf_adder)(@(struct_name)::@(field_name), static_cast<@(field_pbf_type)>(*it));
@[                      else]@
@{                      enum_pkg_and_msg_name = proto_types[tuple(field.type_name.split('.')[1:])] }@
@{                      enum_field_name = naming_convention.enum_field(enum_pkg_and_msg_name) }@
                        dst.@(field_pbf_adder)(@(struct_name)::@(field_name), static_cast<@(enum_pbf_type)>(it->@(enum_field_name)));
@[                      end if]@
                    } else {
                        field_ok = false;
                    }
@[                  else]@
@[                      if field.type != FieldDescriptorProto.Type.TYPE_ENUM]@
                    dst.@(field_pbf_adder)(@(struct_name)::@(field_name), *it);
@[                      else]@
@{                      enum_pkg_and_msg_name = proto_types[tuple(field.type_name.split('.')[1:])] }@
@{                      enum_field_name = naming_convention.enum_field(enum_pkg_and_msg_name) }@
                        dst.@(field_pbf_adder)(@(struct_name)::@(field_name), it->@(enum_field_name));
@[                      end if]@
@[                  end if]@
@[              end if]@
                }
                ok &= field_ok;
@[          end if]@
@[      else]@
@[          if field.type == FieldDescriptorProto.Type.TYPE_MESSAGE]@
@{              field_pkg_and_msg_name = naming_convention.struct(tuple(field.type_name.split('.')[1:])) }@
                ok &= @(field_cpp_package)::@(namespace)::@(encode_decl_name)(src.@(field_name), protozero::basic_pbf_builder<BufferT, @(field_pkg_and_msg_name)>{dst, @(struct_name)::@(field_name)});
@[          elif field.type == FieldDescriptorProto.Type.TYPE_BYTES]@
                dst.@(field_pbf_adder)(@(struct_name)::@(field_name), static_cast<@(field_pbf_type)>(src.@(field_name)).data.data(), static_cast<@(field_pbf_type)>(src.@(field_name)).data.size());
@[          elif field.type == FieldDescriptorProto.Type.TYPE_STRING]@
                dst.@(field_pbf_adder)(@(struct_name)::@(field_name), src.@(field_name));
@[          else]@
@[              if field_needs_cast]@
                const auto value = static_cast<value_type>(src.@(field_name));
                if (min <= value && value <= max) {
@[                  if field.type != FieldDescriptorProto.Type.TYPE_ENUM]@
                    dst.@(field_pbf_adder)(@(struct_name)::@(field_name), static_cast<@(field_pbf_type)>(src.@(field_name)));
@[                  else]@
@{                      enum_field_type = tuple(field.type_name.split('.')[1:]) }@
@{                      enum_field_name = naming_convention.enum_field(enum_field_type) }@
                    dst.@(field_pbf_adder)(@(struct_name)::@(field_name), static_cast<@(field_pbf_type)>(src.@(field_name).@(enum_field_name)));
@[                  end if]@
                } else {
                    ok = false;
                }
@[              else]@
@[                  if field.type != FieldDescriptorProto.Type.TYPE_ENUM]@
                dst.@(field_pbf_adder)(@(struct_name)::@(field_name), src.@(field_name));
@[                  else]@
@{                      enum_field_type = tuple(field.type_name.split('.')[1:]) }@
@{                      enum_field_name = naming_convention.enum_field(enum_field_type) }@
                dst.@(field_pbf_adder)(@(struct_name)::@(field_name), src.@(field_name).@(enum_field_name));
@[                  end if]@
@[              end if]@
@[          end if]@
@[      end if]@
            }
@[  end for]@
@[elif isinstance(message, EnumDescriptorProto)]@
@{  enum_field_name = naming_convention.enum_field(pkg_and_msg_name) }@
@{  _, field_cpp_type, _, field_pbf_type, _, field_pbf_adder, _ = deduce_cpp_type(message, proto_types) }@
            switch (static_cast<@(struct_name)>(src.@(enum_field_name))) {
@[  for value in message.value[:-1]]@
                case @(struct_name)::@(naming_convention.enum_value(pkg_and_msg_name, value.name)):
@[  end for]@
                case @(struct_name)::@(naming_convention.enum_value(pkg_and_msg_name, message.value[-1].name)): {
@[  if field_cpp_type != field_pbf_type]@
                    dst.add_varint(static_cast<@(field_pbf_type)>(src.@(enum_field_name)));
@[  else]@
                    dst.add_varint(src.@(enum_field_name));
@[  end if]@
                    break;
                }
                default: {
                    ok = false;
                    break;
                }
            }
@[else]@
@{  raise RuntimeError(f"Unsupported message type: '{message}'") }@
@[end if]@
        } catch (...) {
            ok = false;
        }
        return ok;
    }

} // namespace @(package_name)::@(namespace)

#endif // @(header_guard)
