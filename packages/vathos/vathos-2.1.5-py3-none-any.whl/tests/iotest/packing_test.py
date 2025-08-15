# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2020-2021, Vathos GmbH
#
# All rights reserved.
#
###############################################################################
import unittest

import numpy as np

from vathos_vision.io.packing import pack_float, unpack_float, pack_short, unpack_short


class TestFloatPacking(unittest.TestCase):

  def setUp(self):
    self.float_array = np.array([[1.0, 2.0, 3.0]], dtype='f')

  def test_pack_and_unnpack(self):
    packed = pack_float(self.float_array)
    unpacked = unpack_float(packed)
    np.testing.assert_array_equal(unpacked, self.float_array)


class TestShortPacking(unittest.TestCase):

  def setUp(self):
    self.short_array = np.array([[1, 2, 3]], dtype='uint16')

  def test_pack_and_unnpack(self):
    packed = pack_short(self.short_array)
    unpacked = unpack_short(packed)
    np.testing.assert_array_equal(unpacked, self.short_array)
