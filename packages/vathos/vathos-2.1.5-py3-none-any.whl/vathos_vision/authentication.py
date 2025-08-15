# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2019-2025, Vathos GmbH
#
# All rights reserved.
#
################################################################################
"""Authentication with the cloud REST API.

To be granted access to its functions, all requests made to the API must include
a valid access token in a special HTTP header. This token identifies a user or
organization. It cannot be replicated or forged and expires after a certain
amount of time.

"""

import requests


def get_client_token(client_id, client_secret, username, password):
  """Get a user token.

  Users who are natural persons require four different credentials for
  authentication which are passed as arguments to this function.

  Args:
    client_id (str): client id
    client_secret (str): client passphrase
    username (str): user id
    password: (str): user password

  Returns:
    str: bearer token which must be passed in the authorization header with 
      every request made to the REST API
  """
  token_response = requests.post(
      'https://auth.gke.vathos.net/auth/realms/picking/protocol' \
        '/openid-connect/token',
      headers={'content-type': 'application/x-www-form-urlencoded'},
      data={
          'client_id': client_id,
          'client_secret': client_secret,
          'username': username,
          'password': password,
          'grant_type': 'password',
      },
      timeout=5)
  return token_response.json()['access_token']


def get_service_account_token(client_id, client_secret):
  """Retrieve a service account token.
  
  A service account is an account not associated with a person but rather a
  device or organization. It can be obtained with the client id and secret
  alone. 

  Args:
    client_id (str): client id
    client_secret (str): client passphrase

  Returns:
    str: bearer token which must be passed in the authorization header with
      every request made to the REST API
  """
  token_response = requests.post(
      'https://auth.gke.vathos.net/auth/realms/picking/protocol' \
        '/openid-connect/token',
      headers={'content-type': 'application/x-www-form-urlencoded'},
      data={
          'client_id': client_id,
          'client_secret': client_secret,
          'grant_type': 'client_credentials',
      },
      timeout=5)
  return token_response.json()['access_token']
