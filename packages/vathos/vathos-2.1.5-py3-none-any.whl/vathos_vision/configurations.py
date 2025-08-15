# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2019-2025, Vathos GmbH
#
# All rights reserved.
#
################################################################################

import requests

from vathos_vision import BASE_URL


def get_configuration(product_id, service, token):
  """Get the most recent inference configuration.
  
  Args:
    product_id (str): id of the product for which the configuration was created
    service (str): name of the inference service for which the configuraton was
      created
    token (str): API access token
  
  Returns:
    dict: configuration data
  """
  url = f'{BASE_URL}/configurations?product={product_id}&service={service}'
  response = requests.get(url,
                          headers={'Authorization': 'Bearer ' + token},
                          timeout=5)
  configurations = response.json()

  if len(configurations) == 0:
    return None
  else:
    # last is the newest
    return configurations[-1]['data']
