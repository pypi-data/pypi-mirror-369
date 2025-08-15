# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2019-2025, Vathos GmbH
#
# All rights reserved.
#
################################################################################
"""File operations."""

from io import BytesIO

import requests

from vathos_vision import BASE_URL


def upload_files(file_list, token, sync=False, device=None):
  """Upload one or multiple files.
  
  Args:
    file_list (list): list of file-like objects or paths

  Returns:
    list: meta data objects of uploaded files
  """
  upload_body = {}
  for i, file in enumerate(file_list):
    if isinstance(file, str):
      # process an image path on disk
      upload_body[f'file_{str(i).zfill(2)}'] = open(file, 'rb')
    else:
      # process file-like object
      upload_body[f'file_{str(i).zfill(2)}'] = file
  if sync:
    url = f'{BASE_URL}/syncblobs'
  elif device is None:
    url = f'{BASE_URL}/blobs'
  else:
    url = f'{BASE_URL}/syncblobs/{device}'
  upload_response = requests.post(url,
                                  files=upload_body,
                                  headers={'Authorization': f'Bearer {token}'},
                                  timeout=120)
  return upload_response.json()


def get_file(file_id, token):
  """Download a file from the REST API.

  Args:
  file_id (str): id of the file to get

  Returns:
    BytesIO: byte representation of the file
  """
  http_request = requests.get(f'{BASE_URL}/blobs/{file_id}',
                              headers={'Authorization': 'Bearer ' + token},
                              stream=True)
  http_request.raw.decode_content = True

  data_buffer = BytesIO(http_request.content)
  data_buffer.seek(0)
  return data_buffer
