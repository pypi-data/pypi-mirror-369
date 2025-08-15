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

#include "../../../ScalableVectorSearch/bindings/python/include/svs/python/vamana.h"

namespace svs::python {
namespace vamana_specializations {

// Compressed search specializations.
// Pattern:
// DistanceType, Primary, Residual, Dimensionality, Strategy, EnableBuild
#define X(Dist, P, R, N, S, B) f.template operator()<Dist, P, R, N, S, B>()
template <typename F> void lvq_specialize_4x0(const F& f) {
    using Sequential = svs::quantization::lvq::Sequential;
    using Turbo = svs::quantization::lvq::Turbo<16, 8>;

    // Sequential
    X(DistanceL2, 4, 0, Dynamic, Sequential, true);
    X(DistanceIP, 4, 0, Dynamic, Sequential, true);
    X(DistanceCosineSimilarity, 4, 0, Dynamic, Sequential, true);
    // Turbo
    X(DistanceL2, 4, 0, Dynamic, Turbo, true);
    X(DistanceIP, 4, 0, Dynamic, Turbo, true);
    X(DistanceCosineSimilarity, 4, 0, Dynamic, Turbo, true);
}

template <typename F> void lvq_specialize_4x4(const F& f) {
    using Sequential = svs::quantization::lvq::Sequential;
    using Turbo = svs::quantization::lvq::Turbo<16, 8>;

    // Sequential
    X(DistanceL2, 4, 4, Dynamic, Sequential, true);
    X(DistanceIP, 4, 4, Dynamic, Sequential, true);
    X(DistanceCosineSimilarity, 4, 4, Dynamic, Sequential, true);
    // Turbo
    X(DistanceL2, 4, 4, Dynamic, Turbo, true);
    X(DistanceIP, 4, 4, Dynamic, Turbo, true);
    X(DistanceCosineSimilarity, 4, 4, Dynamic, Turbo, true);
}

template <typename F> void lvq_specialize_4x8(const F& f) {
    using Sequential = svs::quantization::lvq::Sequential;
    using Turbo = svs::quantization::lvq::Turbo<16, 8>;

    // Sequential
    X(DistanceL2, 4, 8, Dynamic, Sequential, true);
    X(DistanceIP, 4, 8, Dynamic, Sequential, true);
    X(DistanceCosineSimilarity, 4, 8, Dynamic, Sequential, true);
    // Turbo
    X(DistanceL2, 4, 8, Dynamic, Turbo, true);
    X(DistanceIP, 4, 8, Dynamic, Turbo, true);
    X(DistanceCosineSimilarity, 4, 8, Dynamic, Turbo, true);
}

template <typename F> void lvq_specialize_8x0(const F& f) {
    using Sequential = svs::quantization::lvq::Sequential;
    using Turbo = svs::quantization::lvq::Turbo<16, 4>;

    // Sequential
    X(DistanceL2, 8, 0, Dynamic, Sequential, true);
    X(DistanceIP, 8, 0, Dynamic, Sequential, true);
    X(DistanceCosineSimilarity, 8, 0, Dynamic, Sequential, true);
    // Turbo
    X(DistanceL2, 8, 0, Dynamic, Turbo, true);
    X(DistanceIP, 8, 0, Dynamic, Turbo, true);
    X(DistanceCosineSimilarity, 8, 0, Dynamic, Turbo, true);
}

template <typename F> void lvq_specialize_8x8(const F& f) {
    using Sequential = svs::quantization::lvq::Sequential;
    X(DistanceL2, 8, 8, Dynamic, Sequential, false);
    X(DistanceIP, 8, 8, Dynamic, Sequential, false);
    X(DistanceCosineSimilarity, 8, 8, Dynamic, Sequential, false);
}

template <typename F> void compressed_specializations(F&& f) {
    lvq_specialize_4x0(f);
    lvq_specialize_4x4(f);
    lvq_specialize_4x8(f);
    lvq_specialize_8x0(f);
    lvq_specialize_8x8(f);
}
#undef X

// LeanVec specializations.
// Pattern:
// Primary, Secondary, LeanVec Dimensionality, Dimensionality, DistanceType
#define X(P, S, L, N, D) f.template operator()<P, S, L, N, D>()
template <typename F> void leanvec_specialize_unc_unc(const F& f) {
    X(float, float, Dynamic, Dynamic, DistanceL2);
    X(float, float, Dynamic, Dynamic, DistanceIP);
    X(float, float, Dynamic, Dynamic, DistanceCosineSimilarity);

    X(svs::Float16, svs::Float16, Dynamic, Dynamic, DistanceL2);
    X(svs::Float16, svs::Float16, Dynamic, Dynamic, DistanceIP);
    X(svs::Float16, svs::Float16, Dynamic, Dynamic, DistanceCosineSimilarity);
}

template <typename F> void leanvec_specialize_lvq_unc(const F& f) {
    X(svs::leanvec::UsingLVQ<8>, svs::Float16, Dynamic, Dynamic, DistanceL2);
    X(svs::leanvec::UsingLVQ<8>, svs::Float16, Dynamic, Dynamic, DistanceIP);
    X(svs::leanvec::UsingLVQ<8>, svs::Float16, Dynamic, Dynamic, DistanceCosineSimilarity);
}

template <typename F> void leanvec_specialize_lvq_lvq(const F& f) {
    // clang-format off
    X(svs::leanvec::UsingLVQ<4>, svs::leanvec::UsingLVQ<4>, Dynamic, Dynamic, DistanceL2);
    X(svs::leanvec::UsingLVQ<4>, svs::leanvec::UsingLVQ<4>, Dynamic, Dynamic, DistanceIP);
    X(svs::leanvec::UsingLVQ<4>, svs::leanvec::UsingLVQ<4>, Dynamic, Dynamic, DistanceCosineSimilarity);

    X(svs::leanvec::UsingLVQ<4>, svs::leanvec::UsingLVQ<8>, Dynamic, Dynamic, DistanceL2);
    X(svs::leanvec::UsingLVQ<4>, svs::leanvec::UsingLVQ<8>, Dynamic, Dynamic, DistanceIP);
    X(svs::leanvec::UsingLVQ<4>, svs::leanvec::UsingLVQ<8>, Dynamic, Dynamic, DistanceCosineSimilarity);

    X(svs::leanvec::UsingLVQ<8>, svs::leanvec::UsingLVQ<8>, Dynamic, Dynamic, DistanceL2);
    X(svs::leanvec::UsingLVQ<8>, svs::leanvec::UsingLVQ<8>, Dynamic, Dynamic, DistanceIP);
    X(svs::leanvec::UsingLVQ<8>, svs::leanvec::UsingLVQ<8>, Dynamic, Dynamic, DistanceCosineSimilarity);
    // clang-format on
}

template <typename F> void leanvec_specializations(F&& f) {
    leanvec_specialize_unc_unc(f);
    leanvec_specialize_lvq_unc(f);
    leanvec_specialize_lvq_lvq(f);
}
#undef X

} // namespace vamana_specializations
} // namespace svs::python
