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

namespace v1 {

/**
 * Common operation attributes id
 */
enum class operation_attr_id : int {
    version,

    priority,
    to_cache,
    synchronous,
    match_id,

    last_value CCL_DEPRECATED_ENUM_FIELD
};

/**
 * Collective attributes
 */

// To maintain backward compatibility with past releases,
// op_id_offset value starts at 5. It's not necessary for new enums.

enum class allgather_attr_id : int {
    op_id_offset = 5,
};

enum class allgatherv_attr_id : int {
    op_id_offset = 5,
};

enum class allreduce_attr_id : int {
    op_id_offset = 5,

    reduction_fn = op_id_offset,
};

enum class alltoall_attr_id : int {
    op_id_offset = 5,
};

enum class alltoallv_attr_id : int {
    op_id_offset = 5,
};

enum class barrier_attr_id : int {
    op_id_offset = 5,
};

enum class broadcast_attr_id : int {
    op_id_offset = 5,
};

enum class reduce_attr_id : int {
    op_id_offset = 5,

    reduction_fn = op_id_offset,
};

enum class reduce_scatter_attr_id : int {
    op_id_offset = 5,

    reduction_fn = op_id_offset,
};

enum class pt2pt_attr_id : int {
    op_id_offset = 5,

    group_id = op_id_offset,
};

} // namespace v1

using v1::operation_attr_id;

using v1::allgather_attr_id;
using v1::allgatherv_attr_id;
using v1::allreduce_attr_id;
using v1::alltoall_attr_id;
using v1::alltoallv_attr_id;
using v1::barrier_attr_id;
using v1::broadcast_attr_id;
using v1::pt2pt_attr_id;
using v1::reduce_attr_id;
using v1::reduce_scatter_attr_id;

} // namespace ccl
