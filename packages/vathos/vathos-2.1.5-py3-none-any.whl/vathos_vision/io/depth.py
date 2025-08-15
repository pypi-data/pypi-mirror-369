# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2019-2025, Vathos GmbH
#
# All rights reserved.
#
###############################################################################
"""Reading depths image from various file formats."""

from io import BytesIO

from imageio import imread, volread, imwrite, volwrite
import numpy as np

from vathos_vision.io.packing import pack_short, unpack_short


def read_volumetric_tiff(filename):
  """Read a point map from a volumetric TIFF.
  
  This is for example exported by the MechMind viewer. 
  """
  # TIFF stores channels first!
  return np.moveaxis(volread(filename), 0, -1)


def write_volumetric_tiff(filename, point_map):
  """Write a point map to a volumetric TIFF."""
  # TIFF stores channels first!
  volwrite(filename, np.moveaxis(point_map, 2, 0))


def read_from_png_uint8(filename):
  """Read a depth map packed into the RG channels of a PNG-compressed image.
  
  This is the preferred way of storing depth images in all Vathos services.
  """
  rgb_data = imread(filename)
  depth_mm = unpack_short(rgb_data)
  return 0.001 * depth_mm.astype('f')


def write_to_png_uint8(filename, depth):
  """Write a depth map into the RG channels of a PNG-compressed image."""
  depth[np.isnan(depth)] = 0.0
  depth_in_mm = 1000 * depth.astype('f')
  uncompressed_image = pack_short(depth_in_mm.astype('uint16'))
  imwrite(filename, uncompressed_image, format='png')


def write_to_png_uint8_buffer(depth):
  """Pack a float depth image into a PNG-compressed byte buffer."""
  buffer = BytesIO()
  # remove NaNs
  depth[np.isnan(depth)] = 0.0
  depth_in_mm = 1000 * depth.astype('f')
  uncompressed_image = pack_short(depth_in_mm.astype('uint16'))
  imwrite(buffer, uncompressed_image, format='png')
  buffer.name = 'depth.png'
  buffer.seek(0)
  return buffer


def read_from_png_uint16(filename):
  """
  Read a depth map from a 16-bit monochrome image in PNG format.

  Used in academic [datasets](http://redwood-data.org/3dscan/index.html).   
  """
  depth_mm = imread(filename)
  return 0.001 * depth_mm.astype('f')


def write_to_png_uint16(filename, depth):
  """Read a depth map from a 16-bit monochrome image in PNG format.

  Used in academic [datasets](http://redwood-data.org/3dscan/index.html).   
  """
  depth[np.isnan(depth)] = 0.0
  depth_in_mm = 1000 * depth.astype('f')
  imwrite(filename, depth_in_mm.astype('uint16'))
