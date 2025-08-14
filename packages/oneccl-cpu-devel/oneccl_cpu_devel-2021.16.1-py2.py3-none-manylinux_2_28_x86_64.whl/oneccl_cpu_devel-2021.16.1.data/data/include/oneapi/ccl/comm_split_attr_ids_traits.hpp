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

template <>
struct ccl_api_type_attr_traits<comm_split_attr_id, comm_split_attr_id::version> {
    using type = ccl::library_version;
};

template <>
struct ccl_api_type_attr_traits<comm_split_attr_id, comm_split_attr_id::color> {
    using type = int;
};

template <>
struct ccl_api_type_attr_traits<comm_split_attr_id, comm_split_attr_id::group> {
    using type = split_group;
};

} // namespace detail

} // namespace ccl
