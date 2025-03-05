#ifndef ROSIDL_PROTOZERO_RUNTIME__BUILTIN_INTERFACES__PBF__DETAIL__TIME__ENCODE__HPP
#define ROSIDL_PROTOZERO_RUNTIME__BUILTIN_INTERFACES__PBF__DETAIL__TIME__ENCODE__HPP

#include <cstddef>
#include <cstdint>
#include <limits>
#include <type_traits>

#include <protozero/pbf_builder.hpp>
#include <protozero/types.hpp>

#include <builtin_interfaces/msg/duration.hpp>
#include <builtin_interfaces/protozero/detail/google_protobuf__timestamp__tags.hpp>
#include <builtin_interfaces/msg/rosidl_generator_c__visibility_control.h>


namespace builtin_interfaces::pbf {

    template<typename BufferT, typename AllocatorT>
    ROSIDL_GENERATOR_C_PUBLIC_builtin_interfaces
    bool encode(
             const rosidl_protozero_test::protozero::RosidlProtozero_Test_MessageWithCustomFieldOption_<AllocatorT> &src,
             protozero::basic_pbf_builder<BufferT, Time> dst
    ) noexcept {
        bool ok = true;
        try {
            dst.add_int64(Time::seconds, static_cast<std::int64_t>(src.sec));

            if (src.nanosec <= static_cast<std::uint32_t>(std::numeric_limits<std::int32_t>::max())) {
                dst.add_int32(Time::nanos, static_cast<std::int32_t>(src.nanosec));
            } else {
                ok = false;
            }
        } catch (...) {
            ok = false;
        }
        return ok;
    }

} // namespace builtin_interfaces::pbf

#endif // ROSIDL_PROTOZERO_RUNTIME__BUILTIN_INTERFACES__PBF__DETAIL__TIME__ENCODE__HPP
