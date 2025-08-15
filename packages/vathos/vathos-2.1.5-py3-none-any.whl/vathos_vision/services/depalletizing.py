# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2019-2025, Vathos GmbH
#
# All rights reserved.
#
################################################################################
"""Methods to train and run models for depalletizing."""

from io import BufferedReader
import json
import logging
from time import perf_counter

import requests

from vathos_vision import BASE_URL
from vathos_vision.products import get_product
from vathos_vision.configurations import get_configuration
from vathos_vision.files import upload_files
from vathos_vision.io.depth import write_to_png_uint8_buffer


def train_product(product_id, calibration_image, token, device_id=None):
  """Start a training.

  Args:
    product_id (str): id of the product to start the training for. A product
      is created with the function `create_product()` from the module
      `vathos.products`.
    calibration_image (np.ndarray): Depth image of the plane the detected
      objects will rest upon during inference in meters and floating-point
      precision.
    token (str): API access token

  Returns:
    str: id of the training task

  """
  # upload calib image id (synced to device, if available)
  file_data = ('depth.png', write_to_png_uint8_buffer(calibration_image),
               'image/png', {})
  calib_image = upload_files([file_data], token, device=device_id)[0]

  train_data = {
      'workflow':
          'votenet',
      'product':
          product_id,
      'device':
          device_id,
      'tasks': [{
          'service': 'extrinsic.calibration.vathos.net',
          'parameters': {
              'planeImage': calib_image['_id']
          }
      }, {
          'service': 'rendering.votenet.detection.vathos.net'
      }, {
          'service': 'train.votenet.detection.vathos.net'
      }, {
          'service': 'conversion.trt.vathos.net'
      }]
  }

  post_task_response = requests.post(
      f'{BASE_URL}/compositetasks',
      json=train_data,
      headers={'Authorization': f'Bearer {token}'},
      timeout=5)

  return post_task_response.json()['_id']


def run_inference(product_id,
                  test_image,
                  token,
                  score_threshold=0.9999,
                  refine_detections=True):
  """Run an inference request.

  Args:
    product_id (str): id of the product to start the training for. A product
      is created with the function `create_product()` from the module
      `vathos.products`.
    test_image (np.ndarray): float32 image representing the depth in meters
    token (str): API access token

  Returns:
    list: detected objects
  """
  product = get_product(product_id, token)
  configuration = get_configuration(product_id, 'votenet.workflows.vathos.net',
                                    token)
  # overwrite config values with function parameters
  configuration['metric']['conf_thresh'] = score_threshold
  configuration['refine_detections'] = refine_detections
  configuration['icp']['window_size'] = 2000
  configuration['icp']['num_points_icp'] = 50000

  # get depth image for visualization purposes and convert to m
  inference_url = f'{BASE_URL}/workflows/votenet'
  files = {'files': BufferedReader(write_to_png_uint8_buffer(test_image))}
  values = {
      'product': json.dumps(product),
      'configuration': json.dumps(configuration)
  }

  tic = perf_counter()
  inference_response = requests.post(
      inference_url,
      files=files,
      data=values,
      headers={'Authorization': 'Bearer ' + token},
      timeout=20)

  toc = perf_counter()
  logging.info('Inference took %f s', toc - tic)

  inference_response.raise_for_status()

  response_json = inference_response.json()

  return {"product_id": product_id, "detections": response_json['detections']}
