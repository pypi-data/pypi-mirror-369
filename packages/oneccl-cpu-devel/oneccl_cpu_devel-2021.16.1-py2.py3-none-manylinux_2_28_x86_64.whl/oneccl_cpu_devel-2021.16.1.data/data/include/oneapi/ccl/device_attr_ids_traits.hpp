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
#error "Do not include this file directly. Please include 'ccl.hpp'"
#endif

namespace ccl {

namespace detail {

/**
 * Traits for device attributes specializations
 */
template <>
struct ccl_api_type_attr_traits<device_attr_id, device_attr_id::version> {
    using type = library_version;
    using return_type = type;
};

template <>
struct ccl_api_type_attr_traits<device_attr_id, device_attr_id::cl_backend> {
    using type = cl_backend_type;
    using return_type = type;
};

template <>
struct ccl_api_type_attr_traits<device_attr_id, device_attr_id::native_handle> {
    using type = typename unified_device_type::ccl_native_t;
    using return_type = type;
};

} // namespace detail

} // namespace ccl
