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

import vathos_vision.io.depth as depthio


class TestPNGUint8(unittest.TestCase):

  def setUp(self):
    self.float_array = 0.2 * np.ones((512, 512), dtype='f')

  def test_read_and_write(self):
    depthio.write_to_png_uint8('test.png', self.float_array)
    float_array = depthio.read_from_png_uint8('test.png')
    np.testing.assert_array_equal(float_array, self.float_array)


class TestPNGUint16(unittest.TestCase):

  def setUp(self):
    self.float_array = 0.2 * np.ones((512, 512), dtype='f')

  def test_read_and_write(self):
    depthio.write_to_png_uint16('test.png', self.float_array)
    float_array = depthio.read_from_png_uint16('test.png')
    np.testing.assert_array_equal(float_array, self.float_array)


class TestVolumetricTIFF(unittest.TestCase):

  def setUp(self):
    self.float_array = 0.1 * np.ones((512, 512, 2), dtype='f')

  def test_read_and_write(self):
    depthio.write_volumetric_tiff('test.tiff', self.float_array)
    float_array = depthio.read_volumetric_tiff('test.tiff')
    np.testing.assert_array_equal(float_array, self.float_array)
