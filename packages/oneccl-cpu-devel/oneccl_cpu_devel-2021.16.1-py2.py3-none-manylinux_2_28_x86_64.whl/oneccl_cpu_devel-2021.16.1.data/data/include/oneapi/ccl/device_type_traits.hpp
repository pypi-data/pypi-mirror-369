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
#error "Do not include this file directly. Please include 'ccl_type_traits.hpp'"
#endif

#include "oneapi/ccl/native_device_api/export_api.hpp"

namespace ccl {

template <class native_stream>
constexpr bool is_stream_supported() {
    return api_type_info</*typename std::remove_pointer<typename std::remove_cv<*/
                         native_stream /*>::type>::type*/>::is_supported();
}

template <class native_event>
constexpr bool is_event_supported() {
    return api_type_info</*typename std::remove_pointer<typename std::remove_cv<*/
                         native_event /*>::type>::type*/>::is_supported();
}

template <class native_device>
constexpr bool is_device_supported() {
    return api_type_info<typename std::remove_pointer<typename std::remove_cv<
        typename std::remove_reference<native_device>::type>::type>::type>::is_supported();
}

template <class native_context>
constexpr bool is_context_supported() {
    return api_type_info<typename std::remove_pointer<typename std::remove_cv<
        typename std::remove_reference<native_context>::type>::type>::type>::is_supported();
}

/**
 * Export common native API supported types
 */
API_CLASS_TYPE_INFO(empty_t);
API_CLASS_TYPE_INFO(typename unified_device_type::ccl_native_t)
API_CLASS_TYPE_INFO(typename unified_context_type::ccl_native_t);
API_CLASS_TYPE_INFO(typename unified_stream_type::ccl_native_t);
API_CLASS_TYPE_INFO(typename unified_event_type::ccl_native_t);
} // namespace ccl
