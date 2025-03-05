#include <std_msgs/msg/Header.idl>
#include <@(package_name)/msg/@(naming_convention.struct(pkg_and_msg_name)).idl>

module @(package_name) {
    module msg {

@TEMPLATE(
    'struct__constants.idl.em',
    message=message,
    struct_name=naming_convention.stamped_struct(pkg_and_msg_name),
)

@TEMPLATE(
    'struct__stamped.idl.em',
    message=message,
)

    };
};
