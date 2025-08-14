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
class environment;
}

class init_attr_impl;

namespace v1 {

struct ccl_empty_attr;

class init_attr
        : public ccl_api_base_copyable<init_attr, copy_on_write_access_policy, init_attr_impl> {
public:
    using base_t = ccl_api_base_copyable<init_attr, copy_on_write_access_policy, init_attr_impl>;

    /**
     * Declare PIMPL type
     */
    using impl_value_t = typename base_t::impl_value_t;

    /**
     * Declare implementation type
     */
    using impl_t = typename impl_value_t::element_type;

    init_attr& operator=(const init_attr& src);
    init_attr& operator=(init_attr&& src);
    init_attr(init_attr&& src);
    init_attr(const init_attr& src);
    ~init_attr() noexcept;

    /**
     * Set specific value for selft attribute by @attrId.
     * Previous attibute value would be returned
     */
    template <init_attr_id attrId,
              class Value/*,
              class = typename std::enable_if<is_attribute_value_supported<attrId, Value>()>::return_type*/>
    Value set(const Value& v);

    /**
     * Get specific attribute value by @attrId
     */
    template <init_attr_id attrId>
    const typename detail::ccl_api_type_attr_traits<init_attr_id, attrId>::return_type& get() const;

private:
    friend class ccl::detail::environment;
    friend struct ccl::ccl_empty_attr;
    init_attr(const typename detail::ccl_api_type_attr_traits<init_attr_id,
                                                              init_attr_id::version>::return_type&
                  version);
};

/**
 * Declare extern empty attributes
 */
extern init_attr default_init_attr;

/**
 * Fabric helpers
 */
template <init_attr_id t, class value_type>
constexpr auto attr_val(value_type v) -> detail::attr_value_triple<init_attr_id, t, value_type> {
    return detail::attr_value_triple<init_attr_id, t, value_type>(v);
}

} // namespace v1

using v1::init_attr;
using v1::default_init_attr;
using v1::attr_val;

} // namespace ccl
