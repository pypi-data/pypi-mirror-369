# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2019-2025, Vathos GmbH
#
# All rights reserved.
#
################################################################################
"""Image retrieval."""

import requests
from imageio import imread

from vathos_vision import BASE_URL
from vathos_vision.files import get_file
from vathos_vision.io.packing import unpack_short


def get_images(token,
               session=None,
               product=None,
               device=None,
               t_start=None,
               t_end=None,
               limit=100):
  """Retrieve images based on different search criteria."""
  url = f'{BASE_URL}/images?$limit={limit}&%24sort%5Btimestamp%5D=-1'
  if session is not None:
    url += f'&session={session}'
  if product is not None:
    url += f'&product={product}'
  if device is not None:
    url += f'&device={device}'
  if t_start is not None:
    url += f'&timestamp%5B%24gt%5D={t_start}'
  if t_end is not None:
    url += f'&timestamp%5B%24lt%5D={t_end}'

  http_request = requests.get(url,
                              headers={'Authorization': 'Bearer ' + token},
                              timeout=10)
  http_request.raise_for_status()

  return reversed(http_request.json())


def get_detections(image_id, token):
  """Download detections for a given image."""
  url = f'{BASE_URL}/detections?image={image_id}'
  detection_response = requests.get(
      url, headers={'Authorization': 'Bearer ' + token}, timeout=10)
  return detection_response.json()


def get_ir_image(file_id, token):
  """Load and decode an IR image."""
  data = get_file(file_id, token)
  rgb = imread(data, format='PNG')
  temperature_ck = unpack_short(rgb)
  return 0.01 * temperature_ck.astype('f') - 273.15
