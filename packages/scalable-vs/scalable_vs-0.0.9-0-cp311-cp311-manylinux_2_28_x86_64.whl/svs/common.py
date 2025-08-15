# Copyright (C) 2023 Intel Corporation
#
# This software and the related documents are Intel copyrighted materials,
# and your use of them is governed by the express license under which they
# were provided to you ("License"). Unless the License provides otherwise,
# you may not use, modify, copy, publish, distribute, disclose or transmit
# this software or the related documents without Intel's prior written
# permission.
#
# This software and the related documents are provided as is, with no
# express or implied warranties, other than those that are expressly stated
# in the License.

import itertools
import importlib
import struct
import os

import numpy as np

from .public.common import *

def get_lvq_range(data: np.array):
    """
    For a given uncompressed dataset, get the difference between the minimum and maximum
    values for each vector after LVQ-style preprocessing.

    This pre-processing involves removing the component-wise average of the dataset.

    This is not an efficient function.

    Args:
        - data: A 2-D numpy array

    Returns:
        - A 1-D numpy array returning the difference between each vector's maximum and
          minimum component after pre-processing.
    """

    assert(data.ndim == 2)
    center = np.sum(data, axis = 0, dtype = np.float64) / data.shape[0]
    centered_data = data - center

    # Obtain the minimum and maximum values for each dimension.
    mins = np.min(centered_data, axis = 1)
    maxs = np.max(centered_data, axis = 1)
    return maxs - mins
