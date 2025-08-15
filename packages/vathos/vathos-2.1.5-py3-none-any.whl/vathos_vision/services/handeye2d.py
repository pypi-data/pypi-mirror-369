# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2019-2025, Vathos GmbH
#
# All rights reserved.
#
################################################################################

import csv
from datetime import datetime
from time import sleep
import logging

import requests
import numpy as np

from vathos_vision import BASE_URL


def upload_data(csv_file_name, session, token):
  """Uploads images and poses for hand-eye calibration."""

  with open(csv_file_name, 'r', encoding='utf-8') as file:
    reader = csv.reader(file)

    for i, row in enumerate(reader):

      upload_body = {}
      upload_body[f'img_{str(i).zfill(2)}'] = open(row[0], 'rb')

      upload_response = requests.post(
          f'{BASE_URL}/blobs',
          files=upload_body,
          headers={'Authorization': f'Bearer {token}'},
          timeout=60)

      uploaded_file = upload_response.json()[0]

      post_image_response = requests.post(
          f'{BASE_URL}/images',
          json={
              'file': uploaded_file['_id'],
              'session': session,
              'contentType': 'image/png'
          },
          headers={'Authorization': f'Bearer {token}'},
          timeout=5)
      image_id = post_image_response.json()['_id']

      requests.post(f'{BASE_URL}/detections',
                    json={
                        'image': image_id,
                        'frame': [float(r) for r in row[1:]]
                    },
                    headers={'Authorization': f'Bearer {token}'},
                    timeout=5)


def handeye_calibration(poses,
                        projection_matrix,
                        pattern_sidelength,
                        pattern_size,
                        eye_in_hand,
                        token,
                        session=None):
  r"""Run a hand-eye calibration.
  
  Args:
    poses (str): path to a CSV file containing the poses and a reference to the
      associated image. Each row consists of 17 columns. The first column
      contains the path of the image on disk. The following 16 columns store
      the pose of the robot when the image was captured as homogenous
      $4\\times4$ matrix in column-major ordering.
    projection_matrix (numpy.ndarray): a $3\\times 3$ projection matrix of the 
      used camera
    pattern_sidelength (float): length of squares in the pattern in meters
    pattern_size (tuple): number of inner corners of the pattern in horizontal
      and vertical direction
    eye_in_hand: True if the camera is mounted on the end-effector of the robot,
      False for static cameras
    token (str): API access token
    session (str): optional session id under which all calibration images are
      stored
  
  Returns:
    numpy.ndarray: homogenous $4\\times 4$ matrix of the transformation between
      the camera and flange coordinate system (if `eye_in_hand==True`), or the
      camera coordinate system and a fixed robot base (if `eye_in_hand==False`)
  """
  if session is None:
    session = 'handeye_' + datetime.now().isoformat()

  # upload images and poses under that session id
  upload_data(poses, session, token)

  # fill in task parameters
  data = {
      'service': '2d.handeye.calibration.vathos.net',
      'parameters': {
          'eye_in_hand': eye_in_hand,
          'session': session,
          'pattern_size': pattern_size,
          'pattern_side_length': pattern_sidelength,
          'intrinsics': projection_matrix.astype('f').flatten('F').tolist()
      }
  }

  task_request = requests.post(f'{BASE_URL}/tasks',
                               headers={'Authorization': f'Bearer {token}'},
                               json=data,
                               timeout=5)

  task_data = task_request.json()
  logging.info('Started task %s', task_data)

  while True:
    logging.debug('Waiting for task to finish...')
    # poll the task status
    sleep(5.0)
    task_status_request = requests.get(
        f'{BASE_URL}/tasks/{task_data["_id"]}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=5)
    task_data = task_status_request.json()

    # break out of the loop as soon as the task is completed
    if task_data['status'] == 1:
      return np.reshape(np.array(task_data['result']['transform'], dtype='f'),
                        (4, 4), 'F')
    elif task_data['status'] == -1:
      raise RuntimeError('Calibration failed')
