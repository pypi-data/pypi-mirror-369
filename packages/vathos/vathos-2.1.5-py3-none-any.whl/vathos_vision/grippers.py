# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2019-2025, Vathos GmbH
#
# All rights reserved.
#
################################################################################
"""Gripper creation and administration."""

import requests

from vathos_vision import BASE_URL
from vathos_vision.files import upload_files

ALLOWED_UNITS = ['m', 'dm', 'cm', 'mm']


def create_gripper(name, gripper_type, token, model_file_name='', unit=''):
  """Create a gripper and optionally attaches a 3d model to it.

  Args:
    name (str): human-readable name for the new gripper
    gripper_type (str): gripper type, can be 'vacuum' or 'two-finger'
    token (str): API access token
    model_file_name (str): path to a CAD model file on disk. Currently, the only
      supported format is Wavefront OBJ.
    unit (str): unit in which the CAD model is meaured. Must be one of
      `['m', 'dm', 'cm', 'mm']`.

  Returns:
    str: identifier of the created gripper
  """
  json_data = {
      'name': name,
      'type': gripper_type,
  }
  if model_file_name:
    if unit not in ALLOWED_UNITS:
      raise LookupError('Unknown unit')

    # upload model file (globally synced)
    model_id = upload_files([model_file_name], token, sync=True)[0]
    json_data['model'] = model_id
    json_data['unit'] = unit

  # create gripper
  post_gripper_response = requests.post(
      f'{BASE_URL}/grippers',
      json=json_data,
      headers={'Authorization': f'Bearer {token}'},
      timeout=5)

  gripper = post_gripper_response.json()

  return gripper['_id']


def get_gripper(gripper_id, token):
  """Download gripper data.

  Args:
    gripper_id (str): gripper id
    token (str): API access token

  Returns:
    dict: gripper data
  """
  url = f'{BASE_URL}/grippers/{gripper_id}'
  gripper_response = requests.get(url,
                                  headers={'Authorization': 'Bearer ' + token},
                                  timeout=5)
  return gripper_response.json()


def list_grippers(token, verbose=False):
  """List all exisiting grippers.

  Args:
    token (str): API access token
    verbose (bool): whether to return all fields (or just name+id)

  Returns:
    list: gripper data
  """
  gripper_response = requests.get(f'{BASE_URL}/grippers/',
                                  headers={'Authorization': 'Bearer ' + token},
                                  timeout=5)
  all_grippers = gripper_response.json()
  if verbose:
    output_grippers = all_grippers
  else:
    output_grippers = []
    for gripper_entry in all_grippers:
      gripper = {
          'name': gripper_entry['name'],
          '_id': gripper_entry['_id'],
      }
      output_grippers.append(gripper)
  return output_grippers


def create_grip(frame, name, gripper_id, state_id, token, accepted=False):
  """Create a grip.

  Args:
    frame (list): flattened 4x4 list (col major) of the grip frame
    name (str): human-readable name for the new grip
    gripper_id (str): id of the corresponding gripper
    state_id (str): id of the corresponding state
    token (str): API access token
    accepted (bool): whether the grip was visually accepted by the user

  Returns:
    str: identifier of the created grip
  """
  json_data = {
      'frame': frame,
      'name': name,
      'gripper': gripper_id,
      'state': state_id,
      'accepted': accepted
  }

  post_grip_response = requests.post(
      f'{BASE_URL}/grips',
      json=json_data,
      headers={'Authorization': f'Bearer {token}'},
      timeout=5)

  grip = post_grip_response.json()

  return grip['_id']


def get_grip(grip_id, token):
  """Download grip data.

  Args:
    grip_id (str): grip id
    token (str): API access token

  Returns:
    dict: grip data
  """
  url = f'{BASE_URL}/grips/{grip_id}'
  grip_response = requests.get(url,
                               headers={'Authorization': 'Bearer ' + token},
                               timeout=5)
  return grip_response.json()
