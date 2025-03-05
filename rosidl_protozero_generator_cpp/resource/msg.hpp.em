@{
header_guard = naming_convention.header_guard(package_name, 'protozero', *pkg_and_msg_name)
}@
#ifndef @(header_guard)
#define @(header_guard)

#include <@(package_name)/@(naming_convention.struct_tags_header_path(pkg_and_msg_name))>
#include <@(package_name)/@(naming_convention.struct_encode_header_path(pkg_and_msg_name))>
#include <@(package_name)/@(naming_convention.struct_decode_header_path(pkg_and_msg_name))>

#endif // @(header_guard)
