#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
import argparse
import logging

from utils import logger_init
from utils.helpers import get_token
from settings.local import API_EARL
from settings.local import IP4LOGS_ENDPOINT

# initialise the logger
logger = logging.getLogger("__main__")

# set up command-line options
desc = """
Accepts as input an IPv4 address
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '-i', '--ip',
    required=True,
    help="IPv4 address",
    dest='ip'
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test'
)


def main():
    """Obtain a mac address based on IPv4 address."""
    token = get_token()
    if test:
        print(token)

    headers = dict(
        accept='application/json', Authorization=token
    )
    if test:
        print(headers)
    url = '{0}{1}/ip2mac/{2}'.format(
        API_EARL, IP4LOGS_ENDPOINT, ip
    )
    if test:
        print(url)
    resp = requests.get(url=url, headers=headers, verify=False)
    data = resp.json()
    if test:
        print(data)

    logger.info("IP: {0}".format(ip))
    logger.info("MAC: {0}".format(data['mac']))
    for count, item in enumerate(data):
        print(count,item,data[item])


if __name__ == "__main__":
    args = parser.parse_args()
    ip = args.ip
    test = args.test

    if test:
        print(args)


    sys.exit(main())
