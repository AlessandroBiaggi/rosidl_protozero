@[for inc_msg in included_messages]@
#include <@(inc_msg)>
@[end for]@

module @(package_name) {
    module msg {

@TEMPLATE(
    'struct__constants.idl.em',
    message=message,
    struct_name=naming_convention.struct(pkg_and_msg_name),
)

@TEMPLATE(
    'struct.idl.em',
    message=message,
)

    };
};
