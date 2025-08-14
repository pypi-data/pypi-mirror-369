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

#include "oneapi/ccl/types.hpp"

#define CCL_BE_API /*CCL_HELPER_DLL_EXPORT*/

#define CL_BACKEND_TYPE ccl::cl_backend_type::dpcpp_sycl_l0

#include <sycl/sycl.hpp>

namespace ccl {
template <>
struct backend_info<CL_BACKEND_TYPE> {
    static constexpr ccl::cl_backend_type type() {
        return CL_BACKEND_TYPE;
    }
    static constexpr const char* name() {
        return "DPCPP";
    }
};

template <>
struct generic_device_type<CL_BACKEND_TYPE> {
    using handle_t = cl_device_id; //sycl::device;
    using impl_t = sycl::device;
    using ccl_native_t = impl_t;

    generic_device_type(device_index_type id,
                        sycl::info::device_type = sycl::info::device_type::gpu);
    generic_device_type(const sycl::device& device);
    device_index_type get_id() const;
    ccl_native_t& get() noexcept;
    const ccl_native_t& get() const noexcept;

    sycl::device device;
};

template <>
struct generic_context_type<CL_BACKEND_TYPE> {
    using handle_t = cl_context;
    using impl_t = sycl::context;
    using ccl_native_t = impl_t;

    generic_context_type();
    generic_context_type(ccl_native_t ctx);
    ccl_native_t& get() noexcept;
    const ccl_native_t& get() const noexcept;

    ccl_native_t context;
};

template <>
struct generic_platform_type<CL_BACKEND_TYPE> {
    using handle_t = sycl::platform;
    using impl_t = handle_t;
    using ccl_native_t = impl_t;

    generic_platform_type(ccl_native_t& pl);
    ccl_native_t& get() noexcept;
    const ccl_native_t& get() const noexcept;

    ccl_native_t platform;
};

template <>
struct generic_stream_type<CL_BACKEND_TYPE> {
    using handle_t = cl_command_queue;
    using impl_t = sycl::queue;
    using ccl_native_t = impl_t;

    generic_stream_type(ccl_native_t q);
    ccl_native_t& get() noexcept;
    const ccl_native_t& get() const noexcept;

    ccl_native_t queue;
};

template <>
struct generic_event_type<CL_BACKEND_TYPE> {
    using handle_t = cl_event;
    using impl_t = sycl::event;
    using ccl_native_t = impl_t;

    generic_event_type(ccl_native_t e);
    ccl_native_t& get() noexcept;
    const ccl_native_t& get() const noexcept;
    ccl_native_t event;
};

/**
 * Export CL native API supported types
 */
API_CLASS_TYPE_INFO(cl_command_queue);
API_CLASS_TYPE_INFO(cl_context);
API_CLASS_TYPE_INFO(cl_event)
} // namespace ccl
