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
template <class T>
class function_holder {
public:
    function_holder(T in = nullptr) : val(in) {}
    T get() const {
        return val;
    }

private:
    T val;
};
/**
 * Traits for common attributes specializations
 */
template <>
struct ccl_api_type_attr_traits<operation_attr_id, operation_attr_id::version> {
    using type = ccl::library_version;
    using return_type = type;
};

template <>
struct ccl_api_type_attr_traits<operation_attr_id, operation_attr_id::priority> {
    using type = size_t;
    using return_type = type;
};

template <>
struct ccl_api_type_attr_traits<operation_attr_id, operation_attr_id::synchronous> {
    using type = bool;
    using return_type = type;
};

template <>
struct ccl_api_type_attr_traits<operation_attr_id, operation_attr_id::to_cache> {
    using type = bool;
    using return_type = type;
};

template <>
struct ccl_api_type_attr_traits<operation_attr_id, operation_attr_id::match_id> {
    using type = string_class;
    using return_type = type;
};

/**
 * Traits specialization for allgather op attributes
 */

/**
 * Traits specialization for allgatherv op attributes
 */

/**
 * Traits specialization for allreduce op attributes
 */
template <>
struct ccl_api_type_attr_traits<allreduce_attr_id, allreduce_attr_id::reduction_fn> {
    using type = ccl::reduction_fn;
    using return_type = function_holder<type>;
};

/**
 * Traits specialization for alltoall op attributes
 */

/**
 * Traits specialization for alltoallv op attributes
 */

/**
 * Traits specialization for barrier op attributes
 */

/**
 * Traits specialization for broadcast op attributes
 */

/**
 * Traits specialization for pt2pt op attributes
 */
template <>
struct ccl_api_type_attr_traits<pt2pt_attr_id, pt2pt_attr_id::group_id> {
    using type = int;
    using return_type = type;
};

/**
 * Traits specialization for reduce op attributes
 */
template <>
struct ccl_api_type_attr_traits<reduce_attr_id, reduce_attr_id::reduction_fn> {
    using type = ccl::reduction_fn;
    using return_type = function_holder<type>;
};

/**
 * Traits specialization for reduce_scatter op attributes
 */
template <>
struct ccl_api_type_attr_traits<reduce_scatter_attr_id, reduce_scatter_attr_id::reduction_fn> {
    using type = ccl::reduction_fn;
    using return_type = function_holder<type>;
};

} // namespace detail

} // namespace ccl
