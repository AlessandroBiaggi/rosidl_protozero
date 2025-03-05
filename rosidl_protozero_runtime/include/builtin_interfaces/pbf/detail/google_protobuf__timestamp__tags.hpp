#ifndef ROSIDL_PROTOZERO_RUNTIME__BUILTIN_INTERFACES__PBF__DETAIL__TIME__TAGS__HPP
#define ROSIDL_PROTOZERO_RUNTIME__BUILTIN_INTERFACES__PBF__DETAIL__TIME__TAGS__HPP

#include <protozero/types.hpp>

#include <builtin_interfaces/msg/rosidl_generator_c__visibility_control.h>

namespace builtin_interfaces::pbf {

    ROSIDL_GENERATOR_C_PUBLIC_builtin_interfaces
    enum class Time : public protozero::pbf_tag_type {
        seconds = 1,
        nanoseconds = 2,
    };

} // namespace builtin_interfaces::pbf

#endif // ROSIDL_PROTOZERO_RUNTIME__BUILTIN_INTERFACES__PBF__DETAIL__TIME__TAGS__HPP
