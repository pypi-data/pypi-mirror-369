/**
 *    Copyright (C) 2024 Intel Corporation
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

// svs
#include "svs/leanvec/impl/leanvec_impl.h"
#include "svs/quantization/lvq/impl/lvq_impl.h"

#include "svs/python/core.h"

#include "../../../ScalableVectorSearch/bindings/python/include/svs/python/dispatch.h"

template <
    size_t Primary,
    size_t Residual,
    size_t Extent,
    svs::quantization::lvq::LVQPackingStrategy Strategy>
struct svs::lib::DispatchConverter<
    svs::lib::SerializedObject,
    svs::quantization::lvq::LVQLoader<
        Primary,
        Residual,
        Extent,
        Strategy,
        svs::python::RebindAllocator<std::byte>>> {
    using To = svs::quantization::lvq::LVQLoader<
        Primary,
        Residual,
        Extent,
        Strategy,
        svs::python::RebindAllocator<std::byte>>;

    using LVQStrategyDispatch = svs::quantization::lvq::LVQStrategyDispatch;

    static int64_t match(const svs::lib::SerializedObject& object) {
        // TODO: Use a LoadTable directly instead of forcing reparsing every time.
        auto ex = svs::lib::try_load<svs::quantization::lvq::Matcher>(object);
        if (!ex) {
            return svs::lib::invalid_match;
        }

        return svs::quantization::lvq::overload_score<Primary, Residual, Extent, Strategy>(
            ex.value(), LVQStrategyDispatch::Auto
        );
    }

    static To convert(const svs::lib::SerializedObject& object) {
        return To{
            svs::quantization::lvq::Reload{std::move(object.context().get_directory())},
            0,
            svs::python::RebindAllocator<std::byte>()};
    }
};

template <typename PrimaryKind, typename SecondaryKind, size_t LeanVecDims, size_t Extent>
struct svs::lib::DispatchConverter<
    svs::lib::SerializedObject,
    svs::leanvec::LeanVecLoader<
        PrimaryKind,
        SecondaryKind,
        LeanVecDims,
        Extent,
        svs::python::RebindAllocator<std::byte>>> {
    using To = leanvec::LeanVecLoader<
        PrimaryKind,
        SecondaryKind,
        LeanVecDims,
        Extent,
        svs::python::RebindAllocator<std::byte>>;

    static int64_t match(const svs::lib::SerializedObject& object) {
        // TODO: Use a LoadTable directly instead of forcing reparsing every time.
        auto ex = svs::lib::try_load<svs::leanvec::Matcher>(object);
        if (!ex) {
            return svs::lib::invalid_match;
        }

        return svs::leanvec::
            overload_score<PrimaryKind, SecondaryKind, LeanVecDims, Extent>(ex.value());
    }

    static To convert(const svs::lib::SerializedObject& object) {
        return To{
            leanvec::Reload{object.context().get_directory()},
            LeanVecDims, // TODO: This is a hack for now. Since we're reloading, it doesn't
                         // matter.
            std::nullopt,
            0,
            svs::python::RebindAllocator<std::byte>()};
    }
};
