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

#include <sstream>
#include <cstring>
#include <string>
#include <cstdint>

namespace ccl {

namespace v1 {

struct float16 {
    constexpr float16() : data(0) {}
    constexpr float16(uint16_t v) : data(v) {}

    friend bool operator==(const float16& v1, const float16& v2) {
        return (v1.data == v2.data) ? true : false;
    }

    friend bool operator!=(const float16& v1, const float16& v2) {
        return !(v1 == v2);
    }

    uint16_t get_data() const {
        return data;
    }

private:
    uint16_t data;

} __attribute__((packed));

struct bfloat16 {
    constexpr bfloat16() : data(0) {}
    constexpr bfloat16(uint16_t v) : data(v) {}

    friend bool operator==(const bfloat16& v1, const bfloat16& v2) {
        return (v1.data == v2.data) ? true : false;
    }

    friend bool operator!=(const bfloat16& v1, const bfloat16& v2) {
        return !(v1 == v2);
    }

    uint16_t get_data() const {
        return data;
    }

private:
    uint16_t data;

} __attribute__((packed));

} // namespace v1

using v1::float16;
using v1::bfloat16;

} // namespace ccl
