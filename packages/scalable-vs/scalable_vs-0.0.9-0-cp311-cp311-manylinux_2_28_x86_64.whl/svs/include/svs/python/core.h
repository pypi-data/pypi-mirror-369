/**
 *    Copyright (C) 2023 Intel Corporation
 *
 *    This software and the related documents are Intel copyrighted materials,
 *    and your use of them is governed by the express license under which they
 *    were provided to you ("License"). Unless the License provides otherwise,
 *    you may not use, modify, copy, publish, distribute, disclose or transmit
 *    this software or the related documents without Intel's prior written
 *    permission.
 *
 *    This software and the related documents are provided as is, with no
 *    express or implied warranties, other than those that are expressly stated
 *    in the License.
 */

#pragma once

// quantization
#include "svs/leanvec/impl/leanvec_impl.h"
#include "svs/quantization/lvq/impl/lvq_impl.h"

#include "../../../ScalableVectorSearch/bindings/python/include/svs/python/core.h"

namespace svs::python {

/////
///// LVQ
/////

// Compressors - online compression of existing data
using LVQReloader = svs::quantization::lvq::Reload;
using LVQ = svs::quantization::lvq::ProtoLVQLoader<Allocator>;

/////
///// LeanVec
/////

// Dimensionality reduction using LeanVec
using LeanVecReloader = svs::leanvec::Reload;
using LeanVec = svs::leanvec::ProtoLeanVecLoader<Allocator>;

namespace core {
void wrap(pybind11::module& m);
} // namespace core
} // namespace svs::python
