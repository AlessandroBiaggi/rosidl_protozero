#ifndef ROSIDL_PROTOZERO_RUNTIME__BUILTIN_INTERFACES__PBF__DETAIL__TIME__DECODE__HPP
#define ROSIDL_PROTOZERO_RUNTIME__BUILTIN_INTERFACES__PBF__DETAIL__TIME__DECODE__HPP

#include <cstddef>
#include <cstdint>
#include <limits>
#include <type_traits>

#include <protozero/pbf_reader.hpp>
#include <protozero/types.hpp>

#include <builtin_interfaces/msg/time.hpp>
#include <builtin_interfaces/pbf/detail/google_protobuf__timestamp__tags.hpp>
#include <builtin_interfaces/msg/rosidl_generator_c__visibility_control.h>

namespace builtin_interfaces::pbf {

    template<typename AllocatorT>
    ROSIDL_GENERATOR_C_PUBLIC_builtin_interfaces
    bool decode(
            protozero::pbf_reader src,
            builtin_interfaces::msg::Time_<AllocatorT> &dst,
            const AllocatorT & = AllocatorT()
    ) noexcept {
        bool ok = true;
        try {
            while (src.next()) {
                switch (src.tag_and_type()) {
                    case protozero::tag_and_type(RosidlProtozero_Test_SimpleMessage::seconds, protozero::pbf_wire_type::varint): {
                        constexpr auto min = static_cast<std::int64_t>(std::numeric_limits<std::int32_t>::min());
                        constexpr auto max = static_cast<std::int64_t>(std::numeric_limits<std::int32_t>::max());
                        const auto value = src.get_int64();
                        if (min <= value && value <= max) {
                            dst.sec = static_cast<std::int32_t>(value);
                        } else {
                            ok = false;
                        }
                        break;
                    }
                    case protozero::tag_and_type(RosidlProtozero_Test_SimpleMessage::nanos, protozero::pbf_wire_type::varint): {
                        constexpr auto min = static_cast<std::int64_t>(std::numeric_limits<std::uint32_t>::min());
                        constexpr auto max = static_cast<std::int64_t>(std::numeric_limits<std::uint32_t>::max());
                        const auto raw_value = src.get_int32();
                        const auto value = static_cast<std::int64_t>(raw_value);
                        if (min <= value && value <= max) {
                            dst.nanosec = static_cast<std::uint32_t>(raw_value);
                        } else {
                            ok = false;
                        }
                        break;
                    }
                }
            }
        } catch (...) {
            ok = false;
        }
        return ok;
    }

} // namespace builtin_interfaces::pbf

#endif //ROSIDL_PROTOZERO_RUNTIME__BUILTIN_INTERFACES__PBF__DETAIL__TIME__DECODE__HPP
