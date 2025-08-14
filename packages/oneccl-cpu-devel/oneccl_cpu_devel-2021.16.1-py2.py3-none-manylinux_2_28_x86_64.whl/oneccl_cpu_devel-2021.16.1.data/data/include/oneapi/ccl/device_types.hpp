/*
    Copyright Intel Corporation.
    
    This software and the related documents are Intel copyrighted materials, and
    your use of them is governed by the express license under which they were
    provided to you (License). Unless the License provides otherwise, you may
    not use, modify, copy, publish, distribute, disclose or transmit this
    software or the related documents without Intel's prior written permission.
    
    This software and the related documents are provided as is, with no express
    or implied warranties, other than those that are expressly stated in the
    License.
*/
#pragma once

#ifndef CCL_PRODUCT_FULL
#error "Do not include this file directly. Please include 'ccl_types.hpp'"
#endif

#include <map>
#include <set>
#include <limits>

#include "oneapi/ccl/types.hpp"
#include "oneapi/ccl/string.hpp"

namespace ccl {
/* TODO
 * Push the following code into something similar with 'ccl_device_types.hpp'
 */
using index_type = uint32_t;
static constexpr index_type unused_index_value = std::numeric_limits<index_type>::max(); //TODO

//TODO implement class instead
using device_index_type = std::tuple<index_type, index_type, index_type>;
enum device_index_enum { driver_index_id, device_index_id, subdevice_index_id };
ccl::string to_string(const device_index_type& device_id);
device_index_type from_string(const ccl::string& device_id_str);

struct empty_t {};

template <cl_backend_type config_backend>
struct backend_info {};

template <cl_backend_type config_backend>
struct generic_device_type {};

template <cl_backend_type config_backend>
struct generic_context_type {};

template <cl_backend_type config_backend>
struct generic_platform_type {};

template <cl_backend_type config_backend>
struct generic_stream_type {};

template <cl_backend_type config_backend>
struct generic_event_type {};

template <class type>
struct api_type_info {
    static constexpr bool is_supported() {
        return false;
    }
    static constexpr bool is_class() {
        return false;
    }
};

#define API_CLASS_TYPE_INFO(api_type) \
    template <> \
    struct api_type_info<api_type> { \
        static constexpr bool is_supported() { \
            return true; \
        } \
        static constexpr bool is_class() { \
            return std::is_class<api_type>::value; \
        } \
    };
} // namespace ccl

inline std::ostream& operator<<(std::ostream& out, const ccl::device_index_type& index) {
    out << ccl::to_string(index);
    return out;
}
