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

#include "../../../ScalableVectorSearch/bindings/python/include/svs/python/dynamic_vamana.h"

namespace svs::python::dynamic_vamana {

template <typename F> void for_compressed_specializations(F&& f) {
    using Sequential = svs::quantization::lvq::Sequential;
#define X(Dist, Primary, Residual, Strategy, N) \
    f.template operator()<Dist, Primary, Residual, Strategy, N>()
    // Sequential
    X(DistanceL2, 4, 0, Sequential, Dynamic);
    X(DistanceIP, 4, 0, Sequential, Dynamic);
    X(DistanceL2, 4, 4, Sequential, Dynamic);
    X(DistanceIP, 4, 4, Sequential, Dynamic);
    X(DistanceL2, 4, 8, Sequential, Dynamic);
    X(DistanceIP, 4, 8, Sequential, Dynamic);
    X(DistanceL2, 8, 0, Sequential, Dynamic);
    X(DistanceIP, 8, 0, Sequential, Dynamic);

    // Turbo
    using Turbo16x8 = svs::quantization::lvq::Turbo<16, 8>;
    X(DistanceL2, 4, 0, Turbo16x8, Dynamic);
    X(DistanceIP, 4, 0, Turbo16x8, Dynamic);
    X(DistanceL2, 4, 4, Turbo16x8, Dynamic);
    X(DistanceIP, 4, 4, Turbo16x8, Dynamic);
    X(DistanceL2, 4, 8, Turbo16x8, Dynamic);
    X(DistanceIP, 4, 8, Turbo16x8, Dynamic);
#undef X
}

template <typename F> void for_leanvec_specializations(F&& f) {
#define X(Dist, Primary, Secondary, L, N) \
    f.template operator()<Dist, Primary, Secondary, L, N>()
    X(DistanceL2, svs::Float16, svs::Float16, Dynamic, Dynamic);
    X(DistanceIP, svs::Float16, svs::Float16, Dynamic, Dynamic);

    X(DistanceL2, svs::leanvec::UsingLVQ<8>, svs::Float16, Dynamic, Dynamic);
    X(DistanceIP, svs::leanvec::UsingLVQ<8>, svs::Float16, Dynamic, Dynamic);

    X(DistanceL2, svs::leanvec::UsingLVQ<8>, svs::leanvec::UsingLVQ<8>, Dynamic, Dynamic);
    X(DistanceIP, svs::leanvec::UsingLVQ<8>, svs::leanvec::UsingLVQ<8>, Dynamic, Dynamic);

    X(DistanceL2, svs::leanvec::UsingLVQ<4>, svs::leanvec::UsingLVQ<8>, Dynamic, Dynamic);
    X(DistanceIP, svs::leanvec::UsingLVQ<4>, svs::leanvec::UsingLVQ<8>, Dynamic, Dynamic);

    X(DistanceL2, svs::leanvec::UsingLVQ<4>, svs::leanvec::UsingLVQ<4>, Dynamic, Dynamic);
    X(DistanceIP, svs::leanvec::UsingLVQ<4>, svs::leanvec::UsingLVQ<4>, Dynamic, Dynamic);
#undef X
}

} // namespace svs::python::dynamic_vamana
