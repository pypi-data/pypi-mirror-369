# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2019-2025, Vathos GmbH
#
# All rights reserved.
#
###############################################################################

import logging
import os

__version__ = '2.1.5'

root_logger = logging.getLogger(None)
root_logger.handlers = []
logging.basicConfig(
    format=
    '%(asctime)s,%(msecs)d %(levelname)-2s ' \
    '[%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=os.environ.get('LOG_LEVEL', 'INFO'))

BASE_URL = os.environ.get('VATHOS_BASE_URL',
                          'https://api.vathos.net/v1').rstrip('/')

logging.debug('Connecting to %s', BASE_URL)
