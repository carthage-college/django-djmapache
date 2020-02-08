# -*- coding: utf-8 -*-

import requests
import json
import logging

from settings.local import API_EARL
from settings.local import USERNAME
from settings.local import PASSWORD
from settings.local import LOGIN_ENDPOINT


def get_token():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = dict(
        username=USERNAME,
        password=PASSWORD
    )
    url = API_EARL + LOGIN_ENDPOINT
    resp = requests.post(
        url=url, data=json.dumps(params), headers=headers, verify=False
    )
    print(resp.content.decode('utf-8'))

    return json.loads(resp.content.decode('utf-8'))['token']


def get_logger(logger_name):

        # create logger
        log = logging.getLogger(logger_name)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # create file handler for logger.
        fh = logging.FileHandler('{0}.log'.format(logger_name))
        fh.setLevel(level=logging.DEBUG)
        fh.setFormatter(formatter)

        # add handlers to logger.
        log.addHandler(fh)
        return  log
