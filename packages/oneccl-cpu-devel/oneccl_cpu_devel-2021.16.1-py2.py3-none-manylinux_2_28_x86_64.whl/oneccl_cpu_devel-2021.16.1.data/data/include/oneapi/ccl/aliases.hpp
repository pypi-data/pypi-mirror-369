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

#include <array>
#include <functional>
#include <list>
#include <map>
#include <memory>
#include <mutex>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#include "oneapi/ccl/string.hpp"

namespace ccl {
template <class T, class Alloc = std::allocator<T>>
using vector_class = std::vector<T, Alloc>;

template <class T, std::size_t N>
using array_class = std::array<T, N>;

using string_class = ccl::string;

template <class R, class... ArgTypes>
using function_class = std::function<R(ArgTypes...)>;

template <class T, class Allocator = std::allocator<T>>
using list_class = std::list<T, Allocator>;

template <class Key,
          class T,
          class Compare = std::less<Key>,
          class Allocator = std::allocator<std::pair<const Key, T>>>
using map_class = std::map<Key, T, Compare, Allocator>;

using mutex_class = std::mutex;

template <class T1, class T2>
using pair_class = std::pair<T1, T2>;

template <class T>
using reference_wrapper_class = std::reference_wrapper<T>;

template <class... Types>
using tuple_class = std::tuple<Types...>;

template <class T>
using shared_ptr_class = std::shared_ptr<T>;

template <class T>
using unique_ptr_class = std::unique_ptr<T>;
} // namespace ccl
