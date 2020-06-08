#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import json
import logging

import requests
from djmapache.packetfence.settings.local import API_EARL
from djmapache.packetfence.settings.local import LOGIN_ENDPOINT
from djmapache.packetfence.settings.local import PASSWORD
from djmapache.packetfence.settings.local import USERNAME


def get_token():
    """Obtain the authentication token from packetfence API."""
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    auth_params = {
        'username': USERNAME,
        'password': PASSWORD,
    }
    url = API_EARL + LOGIN_ENDPOINT
    resp = requests.post(
        url=url, data=json.dumps(auth_params), headers=headers, verify=False,
    )
    print(resp.content.decode('utf-8'))

    return json.loads(resp.content.decode('utf-8'))['token']


def get_logger(logger_name):
    """Created a simple logger."""
    # create logger
    log = logging.getLogger(logger_name)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    # create file handler for logger.
    fh = logging.FileHandler('{0}.log'.format(logger_name))
    fh.setLevel(level=logging.DEBUG)
    fh.setFormatter(formatter)

    # add handlers to logger.
    log.addHandler(fh)
    return log
