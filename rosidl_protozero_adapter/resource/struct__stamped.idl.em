@{
struct_name = naming_convention.struct(pkg_and_msg_name)
stamped_struct_name = naming_convention.stamped_struct(pkg_and_msg_name)

header_field_name = naming_convention.header_field_name(message.name)
struct_field_name = naming_convention.struct_field_name(message.name)
}@
struct @(stamped_struct_name) {
    std_msgs::msg::Header @(header_field_name);
    @(package_name)::msg::@(struct_name) @(struct_field_name);
};@
