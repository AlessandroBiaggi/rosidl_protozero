@{
import itertools

from google.protobuf.descriptor_pb2 import DescriptorProto, EnumDescriptorProto, FieldDescriptorProto

from rosidl_protozero_adapter.utils import has_field_flag

from rosidl_protozero_generator_cpp import deduce_cpp_type

def is_repeated(f: FieldDescriptorProto, FD=FieldDescriptorProto) -> bool:
    return f.HasField('label') and f.label == FD.Label.LABEL_REPEATED

header_guard = naming_convention.header_guard(package_name, 'protozero', 'detail', *pkg_and_msg_name, 'decode')

namespace = naming_convention.namespace()
struct_name = naming_convention.struct(pkg_and_msg_name)
decode_decl_name = naming_convention.decode_decl()
validate_decl_name = naming_convention.validate_decl()

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

#include <protozero/pbf_reader.hpp>
#include <protozero/types.hpp>

#include <@(package_name)/@(naming_convention.struct_header_path(pkg_and_msg_name))>
#include <@(package_name)/@(naming_convention.struct_tags_header_path(pkg_and_msg_name))>
#include <@(package_name)/@(naming_convention.visibility_control_header_path())>

@[for field_cpp_package, field_type_name in sorted(includes)]@
#include <@(field_cpp_package)/@(naming_convention.struct_decode_header_path(field_type_name))>
@[end for]@

namespace @(package_name)::@(namespace) {

    template<typename AllocatorT>
    @(naming_convention.visibility_control_public())
    bool @(decode_decl_name)(
             protozero::pbf_reader src,
             @(package_name)::msg::@(struct_name)_<AllocatorT> &dst,
             const AllocatorT &alloc = AllocatorT()
    ) noexcept {
        bool ok = true;
        try {
@[if isinstance(message, DescriptorProto)]@
@[  for field in filter(has_field_flag, itertools.chain(message.oneof_decl, message.field))]@
            dst.@(naming_convention.field_flag(pkg_and_msg_name, field.name)) = false;
@[  end for]@
@[  for field in filter(is_repeated, message.field)]@
            dst.@(naming_convention.field(pkg_and_msg_name, field.name)).clear();
@[  end for]@
            while (src.next()) {
                switch (src.tag_and_type()) {
@[  for field in message.field]@
@{      field_name = naming_convention.field(pkg_and_msg_name, field.name) }@
@{      field_cpp_package, field_cpp_type, field_pbf_wire_type, field_pbf_type, field_pbf_getter, _, _ = deduce_cpp_type(field, proto_types) }@
                    case protozero::tag_and_type(@(struct_name)::@(field_name), protozero::pbf_wire_type::@(field_pbf_wire_type)): {
@{      flag_field = message.oneof_decl[field.oneof_index] if field.HasField('oneof_index') else field }@
@[      if has_field_flag(flag_field)]@
                        dst.@(naming_convention.field_flag(pkg_and_msg_name, flag_field.name)) = true;
@[      end if]@
@[      if field.type not in (FieldDescriptorProto.Type.TYPE_MESSAGE, FieldDescriptorProto.Type.TYPE_ENUM, FieldDescriptorProto.Type.TYPE_BYTES, FieldDescriptorProto.Type.TYPE_STRING) and field_pbf_type != field_cpp_type]@
                        using value_type = std::common_type_t<@(field_pbf_type), @(field_cpp_type)>;
                        constexpr auto min = static_cast<value_type>(std::numeric_limits<@(field_cpp_type)>::min());
                        constexpr auto max = static_cast<value_type>(std::numeric_limits<@(field_cpp_type)>::max());
@[      end if]@
@[      if field.label == FieldDescriptorProto.Label.LABEL_REPEATED]@
@[          if field.HasField('options') and field.options.packed]@
@{              assert field.type not in (FieldDescriptorProto.Type.TYPE_MESSAGE, FieldDescriptorProto.Type.TYPE_BYTES, FieldDescriptorProto.Type.TYPE_STRING) }@
                        const auto pi = src.@(field_pbf_getter)();
                        dst.@(field_name).reserve(dst.@(field_name).size() + pi.size());
                        for (auto it = pi.cbegin(); ok && it != pi.cend(); ++it) {
@[              if field.type == FieldDescriptorProto.Type.TYPE_ENUM]@
                            ok &= @(field_cpp_package)::@(namespace)::@(validate_decl_name)(src.@(field_pbf_getter)(), dst.@(field_name).back());
@[              elif field_pbf_type != field_cpp_type]@
                            const auto value = static_cast<value_type>(*it);
                            if (min <= value && value <= max) {
                                (void) dst.@(field_name).emplace_back(static_cast<@(field_cpp_type)>(*it));
                            } else {
                                ok = false;
                            }
@[              else]@
                            (void) dst.@(field_name).emplace_back(*it);
@[              end if]@
                        }
@[          else]@
@[              if field.type in (FieldDescriptorProto.Type.TYPE_MESSAGE, FieldDescriptorProto.Type.TYPE_ENUM)]@
                        (void) dst.@(field_name).emplace_back(alloc);
@[                  if field.type == FieldDescriptorProto.Type.TYPE_MESSAGE]@
                        ok &= @(field_cpp_package)::@(namespace)::@(decode_decl_name)(src.@(field_pbf_getter)(), dst.@(field_name).back(), alloc);
@[                  else]@
@{                      assert field.type == FieldDescriptorProto.Type.TYPE_ENUM }@
                        ok &= @(field_cpp_package)::@(namespace)::@(validate_decl_name)(src.@(field_pbf_getter)(), dst.@(field_name).back());
@[                  end if]@
@[              elif field.type in (FieldDescriptorProto.Type.TYPE_BYTES, FieldDescriptorProto.Type.TYPE_STRING)]@
                        const auto data = src.@(field_pbf_getter)();
@[                  if field.type == FieldDescriptorProto.Type.TYPE_BYTES]@
                        (void) dst.@(field_name).back().layout.dim.emplace_back(alloc);
                        dst.@(field_name).back().layout.dim.at(0).label = {alloc};
                        dst.@(field_name).back().layout.dim.at(0).size = data.size();
                        dst.@(field_name).back().layout.dim.at(0).stride = sizeof(std::byte);
                        dst.@(field_name).back().layout.data_offset = 0;
                        dst.@(field_name).back().data = std::vector<std::byte>(data.data(), data.data() + data.size(), alloc);
@[                  else]@
                        (void) dst.@(field_name).back().assign(data.data(), data.size());
@[                  end if]@
@[              else]@
@[                  if field_pbf_type != field_cpp_type]@
                        (void) dst.@(field_name).emplace_back();
                        const auto raw_value = src.@(field_pbf_getter)();
                        const auto value = static_cast<value_type>(raw_value);
                        if (min <= value && value <= max) {
                            dst.@(field_name).back() = static_cast<@(field_cpp_type)>(raw_value);
                        } else {
                            ok = false;
                        }
@[                  else]@
                        dst.@(field_name).emplace_back(src.@(field_pbf_getter)());
@[                  end if]@
@[              end if]@
@[          end if]@
@[      else]@
@[          if field.type == FieldDescriptorProto.Type.TYPE_MESSAGE]@
                        ok &= @(field_cpp_package)::@(namespace)::@(decode_decl_name)(src.@(field_pbf_getter)(), dst.@(field_name), alloc);
@[          elif field.type == FieldDescriptorProto.Type.TYPE_ENUM]@
                        ok &= @(validate_decl_name)(src.@(field_pbf_getter)(), dst.@(field_name));
@[          elif field.type in (FieldDescriptorProto.Type.TYPE_BYTES, FieldDescriptorProto.Type.TYPE_STRING)]@
                        const auto data = src.@(field_pbf_getter)();
@[              if field.type == FieldDescriptorProto.Type.TYPE_BYTES]@
                        if (dst.@(field_name).layout.dim.empty()) {
                            (void) dst.@(field_name).layout.dim.emplace_back(alloc);
                        } else {
                            dst.@(field_name).layout.dim.resize(1);
                        }
                        dst.@(field_name).layout.dim.at(0).label = {alloc};
                        dst.@(field_name).layout.dim.at(0).size = data.size();
                        dst.@(field_name).layout.dim.at(0).stride = sizeof(std::byte);
                        dst.@(field_name).layout.data_offset = 0;
                        dst.@(field_name).data = {data.data(), data.data() + data.size(), alloc};
@[              else]@
                        (void) dst.@(field_name) = {data.data(), data.size(), alloc};
@[              end if]@
@[          else]@
@[              if field_pbf_type != field_cpp_type]@
                        const auto raw_value = src.@(field_pbf_getter)();
                        const auto value = static_cast<value_type>(raw_value);
                        if (min <= value && value <= max) {
                            dst.@(field_name) = static_cast<@(field_cpp_type)>(raw_value);
                        } else {
                            ok = false;
                        }
@[              else]@
                        dst.@(field_name) = src.@(field_pbf_getter)();
@[              end if]@
@[          end if]@
@[      end if]@
                        break;
                    }
@[  end for]@
                    default: {
                        ok = false;
                        src.skip();
                        break;
                    }
                }
            }
@[elif isinstance(message, EnumDescriptorProto)]@
@{  _, _, _, _, field_pbf_getter, _, _ = deduce_cpp_type(message, proto_types) }@
            ok &= @(validate_decl_name)(src.@(field_pbf_getter)(), dst);
@[else]@
@{  raise RuntimeError(f"Unsupported message type: '{message}'") }@
@[end if]@
        } catch (...) {
            ok = false;
        }
        return ok;
    }

@[if isinstance(message, EnumDescriptorProto)]@
@{  _, field_cpp_type, _, field_pbf_type, _, _, _ = deduce_cpp_type(message, proto_types) }@
    template<typename AllocatorT>
    @(naming_convention.visibility_control_public())
    bool @(validate_decl_name)(
        const @(field_pbf_type) raw_value,
        @(package_name)::msg::@(struct_name)_<AllocatorT> &dst
    ) noexcept {
@[  if field_cpp_type != field_pbf_type]@
        using value_type = std::common_type_t<@(field_pbf_type), @(field_cpp_type)>;
        constexpr auto min = static_cast<value_type>(std::numeric_limits<@(field_cpp_type)>::min());
        constexpr auto max = static_cast<value_type>(std::numeric_limits<@(field_cpp_type)>::max());
        const auto value = static_cast<value_type>(raw_value);
        if (!(min <= value && value <= max)) {
            return false;
        }
@[  end if]@
        switch (static_cast<@(struct_name)>(raw_value)) {
@{  values = list({v.number: v for v in message.value}.values()) }@
@[  for value in values[:-1]]@
            case @(struct_name)::@(naming_convention.enum_value(message.name, value.name)):
@[  end for]@
            case @(struct_name)::@(naming_convention.enum_value(message.name, values[-1].name)): {
@[  if field_cpp_type != field_pbf_type]@
                dst.@(naming_convention.enum_field(pkg_and_msg_name)) = static_cast<@(field_cpp_type)>(raw_value);
@[  else]@
                dst.@(naming_convention.enum_field(pkg_and_msg_name)) = raw_value;
@[  end if]@
                return true;
            }
            default: {
                return false;
            }
        }
    }
@[end if]@

} // namespace @(package_name)::@(namespace)

#endif // @(header_guard)
