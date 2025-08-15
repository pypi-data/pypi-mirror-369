# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2019-2025, Vathos GmbH
#
# All rights reserved.
#
################################################################################
"""Product creation and administration."""

from time import sleep
import logging

import requests

from vathos_vision import BASE_URL
from vathos_vision.files import upload_files

ALLOWED_UNITS = ['m', 'dm', 'cm', 'mm']


def create_product(name, model_file_name, unit, projection_matrix, image_size,
                   image_range, token):
  r"""Create a product and attaches a 3d model file and camera to it.

  Args:
    name (str): human-readable name for the new product
    model_file_name (str): path to a CAD model file on disk. Currently, the only
      supported format is Wavefront OBJ.
    unit (str): unit in which the CAD model is meaured. Must be one of
      `['m', 'dm', 'cm', 'mm']`.
    projection_matrix (numpy.ndarray): a $3\\times 3$ projection matrix of the
      used camera
    image_size (tuple): image width and height in number of pixels
    image_range: (tuple): minimal and maximal depths captured with the camera in
      meters
    token (str): API access token

  Returns:
    str: identifier of the created product
  """
  if unit not in ALLOWED_UNITS:
    raise LookupError('Unknown unit')

  # upload model file (globally synced)
  model_id = upload_files([model_file_name], token, sync=True)[0]

  # create camera
  post_camera_response = requests.post(
      f'{BASE_URL}/cameras',
      json={
          'cameraType': 'manual',
          'intrinsics': projection_matrix.astype('f').flatten('F').tolist(),
          'size': {
              'width': image_size[0],
              'height': image_size[1]
          },
          'range': {
              'min': image_range[0],
              'max': image_range[1]
          }
      },
      headers={'Authorization': f'Bearer {token}'},
      timeout=5)
  camera = post_camera_response.json()

  # create product
  post_product_response = requests.post(
      f'{BASE_URL}/products',
      json={
          'name': name,
          'models': [model_id],
          'unit': unit,
          'camera': camera['_id']
      },
      headers={'Authorization': f'Bearer {token}'},
      timeout=5)

  product = post_product_response.json()

  # run the model analysis task
  post_task_response = requests.post(
      f'{BASE_URL}/tasks',
      json={
          'service': 'model.analysis.vathos.net',
          'product': product['_id']
      },
      headers={'Authorization': f'Bearer {token}'},
      timeout=5)
  task = post_task_response.json()

  # poll the task for completion
  while True:

    logging.debug('Waiting for task to finish...')
    sleep(5.0)
    task_status_request = requests.get(
        f'{BASE_URL}/tasks/{task["_id"]}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=5)
    task_data = task_status_request.json()

    # break out of the loop as soon as the task is completed
    if task_data['status'] == 1:
      break
    elif task_data['status'] == -1:
      raise RuntimeError('Model post-processing failed')

  return product['_id']


def get_product(product_id, token):
  """Download product data.

  Args:
    product_id (str): product id
    token (str): API access token

  Returns:
    dict: product data
  """
  url = f'{BASE_URL}/products/{product_id}?%24populate%5B0%5D=grips' \
    '&%24populate%5B1%5D=states&%24populate%5B1%5D=camera'
  product_response = requests.get(url,
                                  headers={'Authorization': 'Bearer ' + token},
                                  timeout=5)
  return product_response.json()


def list_products(token, verbose=False):
  """List all exisiting products.

  Args:
    token (str): API access token
    verbose (bool): whether to return all fields (or just name+id)

  Returns:
    list: product data
  """
  products_response = requests.get(f'{BASE_URL}/products/',
                                   headers={'Authorization': 'Bearer ' + token},
                                   timeout=5)
  all_products = products_response.json()
  if verbose:
    output_products = all_products
  else:
    output_products = []
    for product_entry in all_products:
      product = {
          'name': product_entry['name'],
          '_id': product_entry['_id'],
      }
      output_products.append(product)
  return output_products


def list_grippers_of_product(product_id, token):
  """List the assigned grippers of a product.

  Args:
    product_id (str): product id
    token (str): API access token
  """
  product = get_product(product_id, token)
  grippers = product['availableGrippers']
  logging.info('Available grippers: %s', grippers)


def add_gripper_to_product(product_id, gripper_id, token):
  """Add a gripper to a product.

  Args:
    product_id (str): product id
    gripper_id (str): gripper id
    token (str): API access token
  """
  product = get_product(product_id, token)

  grippers = product['availableGrippers']

  if gripper_id not in grippers:
    grippers.append(gripper_id)
    logging.info('Gripper added to product.')
  else:
    logging.warning("Gripper is already assigend to product.")

  requests.patch(f'{BASE_URL}/products/{product_id}',
                 json={'availableGrippers': grippers},
                 headers={'Authorization': f'Bearer {token}'},
                 timeout=5)
  logging.info('Available grippers: %s', grippers)


def remove_gripper_from_product(product_id, gripper_id, token):
  """Remove a gripper from a product.

  Args:
    product_id (str): product id
    gripper_id (str): gripper id
    token (str): API access token
  """
  product = get_product(product_id, token)
  grippers = product['availableGrippers']

  if gripper_id in grippers:
    grippers.remove(gripper_id)
  else:
    logging.warning("Gripper is not assigend to product.")

  requests.patch(f'{BASE_URL}/products/{product_id}',
                 json={'availableGrippers': grippers},
                 headers={'Authorization': f'Bearer {token}'},
                 timeout=5)
  logging.info('Available grippers: %s', grippers)
